"""
Code for the data analysis of RQ6 Test Oracles
"""

from src import (
    read_csv, read_config_json,
    pie_chart, horizontal_histogram, horizontal_bar_chart,
    vertical_tables,
    parse_column, data_preprocess, paperids2citation, get_min_max, dict2upsetform, number2camelform
)

 
from scripts import (
    ROOT_DIR,
    FILE_NAME,
    FILE_DIR, 
    CONFIG_DATA_NAME, 
    CONFIG_FIGURE_NAME,
    FIG_SAVING_DIR,
    TAB_SAVING_DIR
)

import pandas as pd
from collections import Counter
import numpy as np
import re
from typing import Literal, Any
import warnings
warnings.filterwarnings("ignore")

def oracle_common(
    df: pd.DataFrame,
    config_data: dict,
    target_headers: str | list, 
    saving_name: str = "rq6_reference_output.tex",        
) -> tuple[dict, str]:
    multi_data, saving_path = data_preprocess(
        df, 
        target_headers, 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )    
    
    referred_outputs = parse_column(multi_data[0])
    paper_idxes = multi_data[1]

    saving_path: str
    output_dict = {}      # Store the type name
    for paper_idx, referred_output in zip(paper_idxes, referred_outputs):
        if len(referred_output) == 0:
            continue
        
        for meta_data in referred_output:
            if isinstance(referred_output, list):
                reference = meta_data
                output_types = ["N/A"]              
            elif isinstance(referred_output, dict):
                reference = meta_data
                output_types = referred_output[meta_data]    # List

            paper_cite = f"\\Paper{number2camelform(int(paper_idx))}"
            for output_type in output_types:
                if reference not in output_dict.keys():
                    output_dict[reference] = [{
                        "output_type": output_type,
                        "paper_ids": [paper_cite],
                        "paper_number": 1
                    }]
                else:   # The reference is existing, then check the existence of the output type
                    if_existing = False
                    for meta_dict in output_dict[reference]:
                        if output_type == meta_dict["output_type"]:
                            meta_dict["paper_ids"].append(paper_cite)
                            meta_dict["paper_number"] += 1
                            if_existing = True
                            break
                    
                    if not if_existing:
                        # The output type does not exist
                        output_dict[reference].append({
                            "output_type": output_type,
                            "paper_ids": [paper_cite],
                            "paper_number": 1
                        })

    # Reformulate the data
    for reference, output_type_data in output_dict.items():
        output_type_data.sort(key=lambda x: x["paper_number"], reverse=True)
        for meta_dict in output_type_data:
            id_list = meta_dict["paper_ids"]
            meta_dict["paper_ids"] = f"\\cite{{{', '.join(str(x) for x in id_list)}}}"

    return output_dict, saving_path

def specification(
    df: pd.DataFrame,
    config_data: dict,
    saving_name: str = "rq6_program_specification.tex",     
) -> None:
    TEMP_CONFIG = {
        "headers": ["Program specifications", "Output types", "Primary studies", "\#"],
        "tab_space": "p{0.25\\columnwidth}  p{0.35\\columnwidth} p{0.38\\columnwidth} c",
    }

    output_dict, saving_path = oracle_common(
        df,
        config_data,
        ["rq6_outputs", "primary_study_id"],
        saving_name
    )


    # Add a line record the number of primary studies for each type of oracle
    add_list = []
    for oracle_type, oracle_data_list in output_dict.items():
        paper_id_collection = []
        for meta_dict in oracle_data_list:
            match = re.search(r"\{(.*)\}", meta_dict["paper_ids"])
            if match:
                content = match.group(1)  # \PaperOneHundredAndFourteen, \PaperOneHundredAndSeventeen
                # 按逗号拆分，并去掉多余空格
                items = [item.strip() for item in content.split(",")]
            paper_id_collection.extend(items)
        temp_num = len(set(paper_id_collection))
        add_list.append((oracle_type, temp_num))  # 临时存成元组 (类型, 数量)


    # 按 temp_num 从大到小排序
    add_list.sort(key=lambda x: x[1], reverse=True)

    # 再格式化成字符串
    add_list = [f"{oracle_type} ({temp_num})" for oracle_type, temp_num in add_list]
    
    add_line = f"""\\cmidrule(lr){{1-4}} \n    
    \\multicolumn{{{len(TEMP_CONFIG['headers'])}}}{{p{{1.2\\columnwidth}}}}{{\\textbf{{Total number 
    of primary studies for each program specification:}} {
        ', '.join(str(x) for x in add_list)
    }}}\\\\"""

    vertical_tables(
        output_dict,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        addition_line=add_line,
        if_cmidrule=True
    )


def oracle(
    df: pd.DataFrame,
    config_data: dict,
    saving_name: str = "rq6_oracle_type.tex",     
) -> None:
    TEMP_CONFIG = {
        "headers": ["Test oracles", "Testing protocols", "Primary studies", "\#"],
        "tab_space": "p{0.2\columnwidth}  p{0.44\columnwidth} p{0.34\columnwidth} c",
    }

    output_dict, saving_path = oracle_common(
        df,
        config_data,
        ["rq6_oracles", "primary_study_id"],
        saving_name
    )

    # Add a line record the number of primary studies for each type of oracle
    add_list = []
    for oracle_type, oracle_data_list in output_dict.items():
        paper_id_collection = []
        for meta_dict in oracle_data_list:
            match = re.search(r"\{(.*)\}", meta_dict["paper_ids"])
            if match:
                content = match.group(1)  # \PaperOneHundredAndFourteen, \PaperOneHundredAndSeventeen
                # 按逗号拆分，并去掉多余空格
                items = [item.strip() for item in content.split(",")]
            paper_id_collection.extend(items)
        temp_num = len(set(paper_id_collection))
        add_list.append((oracle_type, temp_num))  # 临时存成元组 (类型, 数量)

    # 按 temp_num 从大到小排序
    add_list.sort(key=lambda x: x[1], reverse=True)

    # 再格式化成字符串
    add_list = [f"{oracle_type} ({temp_num})" for oracle_type, temp_num in add_list]
    
    add_line = f"""\\cmidrule(lr){{1-4}} \n    
    \\multicolumn{{{len(TEMP_CONFIG['headers'])}}}{{p{{1.2\\columnwidth}}}}{{\\textbf{{Total number 
    of primary studies for each test oracle:}} {
        ', '.join(str(x) for x in add_list)
    }}}\\\\"""
 
    vertical_tables(
        output_dict,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        addition_line=add_line,
        if_cmidrule=True
    )



if __name__ == "__main__":
    PROCEDURE = [
        ("tab", specification),
        ("tab", oracle)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)

    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure)    # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)

    print("\nRQ6 is done. \n")