"Templates for generating Latex Table"

import os


def centering_header(header):
    # if last_one:
    #     return f"\\multicolumn{{1}}{{c}}{{\\textbf{{{header}}}}}"
    # else:
    #     return f"\\multicolumn{{1}}{{c|}}{{\\textbf{{{header}}}}}"
    return f"\\multicolumn{{1}}{{c}}{{\\textbf{{{header}}}}}"

def vertical_tables(
    data: dict[str, dict[str, str]],
    headers: list[str],
    save_path: str,
    tab_space: str   # e.g., p{{0.14\\textwidth}}|c|p{{0.42\\textwidth}}|p{{0.42\\textwidth}}
) -> None:
    """
    --------------------------------------------------
        header0        header1     ...      header2      
    -------------- --------------       --------------
        data 00        data 10     ...      data 20
        data 01        data 11     ...      data 21
           :              :        ...         :
    --------------------------------------------------
    """
    cent_headers = [centering_header(header) for header in headers]
    
    headers_str = " & ".join(map(str, cent_headers))    # Headers
    cmidrule = " ".join([f"\\cmidrule(lr){{{idx+1}-{idx+1}}}" for idx in range(len(headers))])
    
    data_content = ""
    for line_name, line_data_dict in data.items():
        data_content_list = [line_name]
        for metadata_content in line_data_dict.values():
            data_content_list.append(metadata_content)
        line_content = " & ".join(data_content_list)
        line_content = f"{line_content} \\\\ \n    "
        data_content = f"{data_content}{line_content}"


    latex_code = f"""
\\begin{{tabular}}{{{tab_space}}}
    \\toprule[1pt]

    {headers_str} \\\\
    
    {cmidrule}  

    {data_content}

    \\bottomrule[1pt]
\\end{{tabular}}
    """

    # Make sure the folder where the path is saved exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save the string to a file
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print(f"LaTeX code saved to {save_path}")