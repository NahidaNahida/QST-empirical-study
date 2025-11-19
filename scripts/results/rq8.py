"""
Code for the data analysis of RQ8 Statistical Repetitions
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
import os

import warnings
warnings.filterwarnings("ignore")

def shot_configuration_types(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq8_shot_config_types.pdf",        
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3, 2.5),
        "explode": None,
        "startangle": 90,
        "offset": 0.25,
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq8_shots", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    saving_path: str
    shot_configs = parse_column(req_data)
    num_of_studies = 0

    type_list = []      # Store the type name
    for shot_config in shot_configs:
        # Skip the invalid data
        if len(shot_config) == 0:
            continue

        num_of_studies += 1
        for meta_config in shot_config:
            if isinstance(meta_config, str):
                type_list.append(meta_config)
            elif isinstance(meta_config, dict):
                type_list.append(list(meta_config.keys())[0])

    prop_of_studies = f"{num_of_studies / len(req_data) * 100:.1f}%"
    pie_chart(
        type_list,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_explode=TEMP_CONFIG["explode"],
        fig_startangle=TEMP_CONFIG["startangle"],
        fig_offset=TEMP_CONFIG["offset"],
        title=f"Prop. of primary studies: {num_of_studies}/{len(req_data)} ({prop_of_studies})",       
    )    

def fixed_shots_number(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq8_fixed_shots.pdf",                
):
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3, 2.5),
        "bar_height": 0.25,
        "color": "#B7B5B7F8",
        "target_name": "Fixed"
    }

    req_data, saving_path = data_preprocess(
        df, 
        "rq8_shots", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    saving_path: str
    shot_configs = parse_column(req_data)

    number_list = []      # Store the type name
    for shot_config in shot_configs:
        # Skip the invalid data
        if len(shot_config) == 0:
            continue
        for shot_type, shot_number in shot_config.items():
            if shot_type == TEMP_CONFIG["target_name"]:
                for meta_shot in shot_number:
                    try:
                        number_list.append(int(meta_shot))
                    except (ValueError, TypeError):
                        pass
 
    horizontal_bar_chart(
        number_list, 
        {"x": "# of primary studies", "y": "# of fixed shots"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barheight=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"]
    )

def varied_and_adaptive_shots(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq8_varied_and_adaptive_shots.tex",    
) -> None:
    
    # Instant configuration
    TEMP_CONFIG = {
        "headers": ["Types", "Configurations", "Primary studies"],
        "tab_space": "p{0.13\\columnwidth}  p{0.68\\columnwidth} p{0.20\\columnwidth}",
        "target_names": ["Varied", "Adaptive"]
    }

    multi_data, saving_path = data_preprocess(
        df, 
        ["rq8_shots", "primary_study_id"], 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )    
    
    saving_path: str
    shot_configs = parse_column(multi_data[0])
    paper_idxes = multi_data[1]

    final_config = {}     # Store the type name
    for paper_idx, shot_config in zip(paper_idxes, shot_configs):
        if len(shot_config) == 0:       # Skip the invalid data
            continue

        for current_shot_type in TEMP_CONFIG["target_names"]:
            if current_shot_type not in shot_config.keys():
                continue
            
            if current_shot_type not in final_config.keys():
                final_config[current_shot_type] = []
            
            final_temp_list = final_config[current_shot_type]
 
            config_str = ",".join(str(elem) for elem in shot_config[current_shot_type])
            if len(final_temp_list) == 0:
                final_temp_list.append(
                    {
                        "config": config_str,
                        "paper_ids": [paper_idx],
                        # "paper_number": 1
                    }
                )
            else:
                if_existing = False
                for temp_dict in final_temp_list:
                    if config_str == temp_dict["config"]:  # Existing
                        temp_dict["paper_ids"].append(paper_idx)
                        # temp_dict["paper_number"] += 1
                        if_existing = True
                        break
                if not if_existing:   # Add as new
                    final_temp_list.append(
                        {
                            "config": config_str,
                            "paper_ids": [paper_idx],
                            # "paper_number": 1
                        }
                    )

    # Reformulate the data form
    for shot_config_list in final_config.values():
        # ✅ 按 "paper_number" 从大到小排序
        shot_config_list.sort(
            key=lambda x: len(x.get("paper_ids", [])),
            reverse=True
        )

        for meta_config_dict in shot_config_list:
            target_list = meta_config_dict["paper_ids"].copy()
            trans_list = [
                f"\\Paper{number2camelform(int(paper_idx))}"
                for paper_idx in target_list
            ]
            meta_config_dict["paper_ids"] = (
                f"\\cite{{{', '.join(str(x) for x in trans_list)}}}"
            )

    vertical_tables(
        final_config,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        if_cmidrule=True
    )
 

def number_of_repetitions(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq8_number_of_repetitions.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (6, 2),
        "bar_height": 0.25,
        "color": "#FFFCCEF8",
        "interval": 50,
        "uplimit": 500
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq8_repetitions", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    saving_path: str

    # Parse the data
    req_data = parse_column(req_data)

    # Collect possible types
    repetition_counts = []
    num_of_studies = 0
    for paper_data in req_data:
        if len(paper_data) == 0:  # Skip invalid data
            continue
        paper_data: list[str]
        num_of_studies += 1
        repetition_counts.extend([int(meta_data) for meta_data in paper_data])
 
    prop_of_studies = f"{num_of_studies / len(req_data) * 100:.1f}%"

    # Generate the intervals
    intervals = list(range(0, TEMP_CONFIG["uplimit"] + 1,TEMP_CONFIG["interval"]))

    # Produce the histogram
    horizontal_histogram(
        repetition_counts, 
        {"x": "# of primary studies", "y": "# of individual repetitions"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barheight=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"],
        title=f"Prop. of primary studies: {num_of_studies}/{len(req_data)} ({prop_of_studies})",
        bins=intervals,
        upper_limit=TEMP_CONFIG["uplimit"]
    )

if __name__ == "__main__":
    PROCEDURE = [
        ("fig", number_of_repetitions),
        ("fig", shot_configuration_types),
        ("tab", varied_and_adaptive_shots),
        ("fig", fixed_shots_number)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data) # type: ignore

    print("\nRQ8 is done. \n")