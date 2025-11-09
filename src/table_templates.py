"Templates for generating Latex Table"

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
    if_cmidrule: bool = False   # \cmidrule follows multiple rows
) -> None:
    r"""
    Generate vertical LaTeX tables from nested dictionaries.

    Supported structures
    ====================

    1️⃣  Simple dict of dicts:
        { data00: {X: data10, Y: data20}, data01: {X: data11, Y: data21} }

    --------------------------------------------------
        header0        header1     ...      header2      
    -------------- --------------       --------------
        data00         data10     ...      data20
        data01         data11     ...      data21
           :              :        ...         :
    --------------------------------------------------

    2️⃣  Dict of list[dict]:
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
    n_cols = len(headers)

    for line_name, line_data in data.items():
        # Case 1️⃣: inner value is a dict
        if isinstance(line_data, dict):
            values = list(line_data.values())
            data_content += f"{line_name} & " + " & ".join(map(str, values)) + " \\\\ \n    "

        # Case 2️⃣: inner value is a list of dicts
        elif isinstance(line_data, list):
            n_rows = len(line_data)
            for idx, sub_dict in enumerate(line_data):
                values = list(sub_dict.values())
                if idx == 0:
                    data_content += (
                        f"{line_name} & "
                        + " & ".join(map(str, values))
                        + " \\\\ \n    "
                    )
                else:
                    data_content += " & " + " & ".join(map(str, values)) + " \\\\ \n    "
            # ✅ add cmidrule across all columns if requested, but not for the last block
            if if_cmidrule and line_name != list(data.keys())[-1]:
                data_content += f"\\cmidrule(lr){{1-{n_cols}}} \n    "
        else:
            raise ValueError(f"Unsupported data type for key '{line_name}': {type(line_data)}")

    if addition_line is not None:
        addition_line = f" \\\\ \n    {addition_line}"
    else:
        addition_line = ""

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


 
def vertical_grouped_table(
    data: dict,
    save_path: str,
    tab_space: str = "c|c",  # 一行显示多少列，通常根据子字典长度
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

        # 顶层 key 作为组标题
        content_lines += f"""
    \\multicolumn{{{num_columns}}}{{l}}{{\\textbf{{{key}:}}}} \\\\
    """

        # 子元素内容
        if isinstance(val_list, list):
            for sub_dict in val_list:
                content_lines += " & ".join(str(v) for v in sub_dict.values()) + " \\\\\n    "
        elif isinstance(val_list, dict):
            content_lines += " & ".join(str(v) for v in val_list.values()) + " \\\\\n    "

        # ✅ 如果不是最后一个 key，再加分割线
        if idx < n_keys - 1 or idx == n_keys - 1 and addition_line is not None:
            content_lines += f"\\cmidrule(lr){{1-{num_columns}}}\n"

    # 可选额外行
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