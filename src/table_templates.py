"""
Docstring for src.table_templates
Templates for various types of tables used in data presentation.
"""

import os, re

def count_latex_columns(col_def: str) -> int:
    """
    Count columns in a LaTeX tabular column definition string.

    Examples handled:
      - c l r
      - p{...}  (also p{{...}})
      - m{...}, b{...}, X{...}
      - ignores '|' and spaces
      - removes >{...} and <{...} modifiers before counting

    Returns: int number of columns
    """
    if not isinstance(col_def, str):
        raise TypeError("col_def must be a string")

    s = col_def.strip()

    # remove spaces and vertical bars (separators)
    s = s.replace(" ", "").replace("|", "")

    # remove modifiers like >{...} and <{...} because they are not columns
    # use non-greedy match for {...}, allow nested repeated braces like >{{...}}
    s = re.sub(r'[<>]\{+.*?\}+', '', s, flags=re.DOTALL)

    # pattern to match:
    #  - parameterized columns: p{...}, m{...}, b{...}, X{...}
    #    (support one-or-more opening braces and corresponding closing braces)
    #  - simple columns: c, l, r (single letters)
    pattern = re.compile(r'(?:[pmbX]\{+.*?\}+|[clr])', flags=re.DOTALL)

    matches = pattern.findall(s)
    return len(matches)

def centering_header(header):
    # if last_one:
    #     return f"\\multicolumn{{1}}{{c}}{{\\textbf{{{header}}}}}"
    # else:
    #     return f"\\multicolumn{{1}}{{c|}}{{\\textbf{{{header}}}}}"
    return f"\\multicolumn{{1}}{{c}}{{\\textbf{{{header}}}}}"

def vertical_tables(
    data: dict,
    headers: list[str],
    save_path: str,
    tab_space: str,   # e.g., p{{0.14\\textwidth}}|c|p{{0.42\\textwidth}}|p{{0.42\\textwidth}}
    addition_line: str | None = None,
    if_cmidrule: bool = False,   # \cmidrule follows multiple rows
    if_midrule_each_line: bool = False
) -> None:
    r"""
    Generate vertical LaTeX tables from nested dictionaries.

    Supported structures
    ====================

    + Simple dict of dicts:
        { data00: {X: data10, Y: data20}, data01: {X: data11, Y: data21} }

    --------------------------------------------------
        header0        header1     ...      header2      
    -------------- --------------       --------------
        data00         data10     ...      data20
        data01         data11     ...      data21
           :              :        ...         :
    --------------------------------------------------

    + Dict of list[dict]:
        { data00: [ {X: data10, Y: data20}, {X: data11, Y: data21} ] }

    --------------------------------------------------
        header0        header1     ...      header2      
    -------------- --------------       --------------
        data00         data10     ...      data20
                       data11     ...      data21
           :              :        ...         :
    --------------------------------------------------

    Extra options
    =============
    - addition_line: Optional LaTeX line added before \bottomrule
    - if_cmidrule: If True, add \cmidrule(lr){1-N} after each multirow block
    """
    cent_headers = [centering_header(header) for header in headers]
    headers_str = " & ".join(map(str, cent_headers))
    cmidrule_header = " ".join([f"\\cmidrule(lr){{{idx+1}-{idx+1}}}" for idx in range(len(headers))])

    data_content = ""
 

    for line_name, line_data in data.items():
        # Case 1: inner value is a dict
        if isinstance(line_data, dict):
            values = list(line_data.values())
            data_content += f"{line_name} & " + " & ".join(map(str, values)) + " \\\\ \n    "
            if if_midrule_each_line == True and line_name != list(data.keys())[-1]:
                # data_content += f"\\cmidrule(lr){{1-{n_cols}}} \n    "
                data_content += f"{cmidrule_header} \n"
        # Case 2: inner value is a list of dicts
        elif isinstance(line_data, list):
            for idx, sub_dict in enumerate(line_data):
                values = list(sub_dict.values())
                if idx == 0:
                    data_content += (
                        f"{line_name} & "
                        + " & ".join(map(str, values))
                        + " \\\\ \n    "
                    )
                else:
                    if line_name != list(data.keys())[-1]:
                        data_content += " & " + " & ".join(map(str, values)) + " \\\\ \n    "
                    else:
                        data_content += " & " + " & ".join(map(str, values)) + " \\\\    "
                    if if_midrule_each_line == True and line_name != list(data.keys())[-1]:
                        # data_content += f"\\cmidrule(lr){{1-{n_cols}}} \n    "
                        data_content += f"{cmidrule_header} \n        "
                        
            # Add cmidrule across all columns if requested, but not for the last block
            if if_cmidrule and line_name != list(data.keys())[-1]:
                # data_content += f"\\cmidrule(lr){{1-{n_cols}}} \n    "
                data_content += f"{cmidrule_header} \n    "
        else:
            raise ValueError(f"Unsupported data type for key '{line_name}': {type(line_data)}")

    # if addition_line is not None:
    #     addition_line = f" \\\\ \n    {addition_line}"
    if addition_line is not None:
        addition_line = f"\n    {addition_line}"
    else:
        addition_line = ""

    # Remove trailing spaces and newlines
    data_content = data_content.rstrip()

    latex_code = f"""
\\begin{{tabular}}{{{tab_space}}}
    \\toprule[1pt]
    {headers_str} \\\\
    {cmidrule_header}  
    {data_content}{addition_line}
    \\bottomrule[1pt]
\\end{{tabular}}
        """

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"LaTeX code saved to {save_path}")


 
def vertical_grouped_table(
    data: dict,
    save_path: str,
    tab_space: str = "c|c",  # Number of columns per row, usually depends on sub-dictionary length
    addition_line: str | None = None
):
    """
    Generate a LaTeX vertical table:
    - Each top-level key is a separate row (like a group header)
    - Each value dict (or list of dicts) is displayed row-wise under the key
    """
    content_lines = ""
 
    num_columns = count_latex_columns(tab_space)
   
    keys = list(data.keys())
    n_keys = len(keys)

    for idx, key in enumerate(keys):
        val_list = data[key]

        # Top-level key as group header
        content_lines += f"""
    \\multicolumn{{{num_columns}}}{{l}}{{\\textbf{{{key}:}}}} \\\\
    """

        # Sub-item content
        if isinstance(val_list, list):
            for sub_dict in val_list:
                content_lines += " & ".join(str(v) for v in sub_dict.values()) + " \\\\\n    "
        elif isinstance(val_list, dict):
            content_lines += " & ".join(str(v) for v in val_list.values()) + " \\\\\n    "

        # Add separator line if not the last key, or if it is the last key and addition_line is provided
        if idx < n_keys - 1 or idx == n_keys - 1 and addition_line is not None:
            content_lines += f"\\cmidrule(lr){{1-{num_columns}}}\n"

    # Optional additional line
    if addition_line is None:
        addition_line = ""
    
    latex_code = f"""
\\begin{{tabular}}{{{tab_space}}}
    \\toprule[1pt]
    {content_lines}
    {addition_line}
    \\bottomrule[1pt]
\\end{{tabular}}
"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    
    print(f"LaTeX code saved to {save_path}")

def two_dimensional_table(
    data_dict: dict[str, dict[str, str]],
    save_path: str
) -> None:
    # Rows and columns (sorted by dictionary keys; can be changed to list(...) to preserve original order)
    rows = sorted(data_dict.keys())

    col_set = set()
    for r in rows:
        col_set.update(data_dict[r].keys())
    cols = sorted(col_set)

    # Column alignment: first column c, remaining columns c
    tab_space = "c|" + "c" * len(cols)

    # Table header (first row)
    headers_str = " & ".join([""] + cols)  # First cell is empty because it corresponds to row names

    # cmidrule
    # If there are C column headers, use: \cmidrule(r){2-<C+1>}
    cmidrule_header = rf"\cmidrule(r){{2-{len(cols)+1}}}"

    # Data content
    lines = []
    for r in rows:
        row_vals = [r]  # First column is the row name
        for c in cols:
            row_vals.append(data_dict[r].get(c, ""))
        lines.append(" & ".join(row_vals) + "\\\\")
    data_content = "\n    ".join(lines)

    # Add an extra line here if needed
    addition_line = ""  # Empty by default

    # Full LaTeX template
    latex_code = f"""
\\begin{{tabular}}{{{tab_space}}}
    \\toprule[1pt]
    {headers_str} \\\\
    {cmidrule_header}  
    {data_content}
    {addition_line}
    \\bottomrule[1pt]
\\end{{tabular}}
    """

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex_code)
    
    print(f"LaTeX code saved to {save_path}")
