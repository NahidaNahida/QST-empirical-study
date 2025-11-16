"""
Code for the data analysis of RQ5 Test Cases
"""

from src import (
    read_csv, read_config_json,
    horizontal_stacked_bar_chart, upset_plot,
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
import os

import warnings
warnings.filterwarnings("ignore")

def whether_reporting_test_counts(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq5_whether_counts.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (6, 0.5),
        "annote_color": "black"
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq5_whether_counts", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    counts_boolean = parse_column(req_data)    
    # Replace "Y" to "Yes" and "N" to "No"
    counts = [0, 0]
    labels = ["Yes", "No"]
    for meta_data in counts_boolean:
        if meta_data[0].lower() == "y":
            counts[0] += 1
        elif meta_data[0].lower() == "n":
            counts[1] += 1

    saving_path = os.path.join(ROOT_DIR, *FIG_SAVING_DIR, saving_name)
    horizontal_stacked_bar_chart(
        counts,
        labels,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_anno_color=TEMP_CONFIG["annote_color"]
    )    


def input_type_distribution(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq5_input_type_distribution.pdf",
) -> None:
    # Instant configuration
    TEMP_CONFIG_UPSET = {
        "figsize": (5, 2.5),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color": "black",
        "wspace": 0.5
    }
    
    # Get the target data
    req_data, saving_path = data_preprocess(
        df, 
        "rq5_input_types",         
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    ) # type: ignore
    saving_path: str

    input_types = parse_column(req_data, skip_invalid_value=False)  # Including invalid values

    # Collect possible types
    category_counts = []
    for paper_data in input_types:
        if len(paper_data) == 0:  # Skip invalid data
            continue
        paper_data: list

        if isinstance(paper_data, str):
            category_counts.extend(paper_data)
        elif isinstance(paper_data, dict):
            category_counts.extend(list(paper_data.keys()))

    categories = list(set(category_counts))

    # Generate the required dictionary for upset plotting
    input_type_dict = {category: [] for category in categories}
    for paper_data in input_types:
        for category in categories:
            current_data = {}
            if category in paper_data.keys(): # type: ignore
                current_data = paper_data[category]
            input_type_dict[category].append(current_data)
        
 
    # Analyse the upset relation
    combo_list, count_list = dict2upsetform(input_type_dict)    
 
    # Generate the upset plot
    upset_plot(
        {"memberships": combo_list, "values": count_list}, 
        # {"x": "# of primary studies", "y": "# of intersaction"},
        saving_path,
        config_figure,
        fig_color=TEMP_CONFIG_UPSET["color"],
        fig_figsize=TEMP_CONFIG_UPSET["figsize"],
        fig_wspace=TEMP_CONFIG_UPSET["wspace"]
    )

def input_type_name(    
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq5_input_type_names.tex",
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "headers": ["Test input types", "Input properties", "Primary studies", "\#"],
        "tab_space": "p{0.25\\columnwidth}  p{0.35\\columnwidth} p{0.38\\columnwidth} c",
    }
    
    # Get the target data
    multi_data, saving_path = data_preprocess(
        df, 
        ["rq5_input_types", "primary_study_id"],         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    ) # type: ignore
    saving_path: str

    input_types = parse_column(multi_data[0])  # excluding invalid values
    paper_idxes = multi_data[1]

    input_type_dict = {}
    # Generate the required dictionary for upset plotting
    for paper_idx, input_type in zip(paper_idxes, input_types):
        if len(input_type) == 0:
            continue
            
        for meta_data in input_type:
            meta_data: dict
            input_name = meta_data
            input_properties = input_type[meta_data]
        
            paper_cite = f"\\Paper{number2camelform(int(paper_idx))}"

            for input_property in input_properties:
                if input_name not in input_type_dict.keys():
                    input_type_dict[input_name] = [{
                        "input_property": input_property,
                        "paper_ids": [paper_cite],
                        "paper_number": 1
                    }]
                else:
                    if_existing = False
                    for meta_dict in input_type_dict[input_name]:
                        if input_property == meta_dict["input_property"]:
                            meta_dict["paper_ids"].append(paper_cite)
                            meta_dict["paper_number"] += 1
                            if_existing = True
                            break
                    
                    if not if_existing:
                        input_type_dict[input_name].append({
                            "input_property": input_property,
                            "paper_ids": [paper_cite],
                            "paper_number": 1
                        })

    # Reformulate the data
    for output_type_data in input_type_dict.values():
        output_type_data.sort(key=lambda x: x["paper_number"], reverse=True)
        for meta_dict in output_type_data:
            id_list = meta_dict["paper_ids"]
            meta_dict["paper_ids"] = f"\\cite{{{', '.join(str(x) for x in id_list)}}}"
 

    vertical_tables(
        input_type_dict,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        if_cmidrule=True
    )



if __name__ == "__main__":
    PROCEDURE = [
        ("fig", whether_reporting_test_counts),
        ("fig", input_type_distribution),
        ("tab", input_type_name)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data) # type: ignore

    print("\nRQ5 is done. \n")