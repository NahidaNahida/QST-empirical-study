"""
Code for the data analysis of RQ9 Execution Backends
"""

from src import (
    read_csv, read_config_json,
    line_chart_general, bar_chart_general, upset_plot, horizontal_stacked_bar_chart,
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

def backend_types(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq9_number_of_backends.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (4, 2.5),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color": "black",
        "wspace": 3
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq9_backend_type", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    # Parse the data
    req_data = parse_column(req_data)

    # Collect possible types
    category_counts = []
    for paper_data in req_data:
        if len(paper_data) == 0:  # Skip invalid data
            continue
        paper_data: list[str]
        category_counts.extend([meta_data for meta_data in paper_data])

    candidate_categories = set(category_counts)
    parsed_data_dict = {category: [] for category in candidate_categories}
    # Load data to dict
    for paper_data in req_data:
        for temp_category in candidate_categories:
            current_val = {}    # For not used
            if len(paper_data) > 0 and temp_category in paper_data:
                current_val = "Used"   # For used
            parsed_data_dict[temp_category].append(current_val)
    
    # Analyse the upset relation
    combo_list, count_list = dict2upsetform(parsed_data_dict)    
    
    # Generate the upset plot
    upset_plot(
        {"memberships": combo_list, "values": count_list}, 
        # {"x": "# of primary studies", "y": "# of intersaction"},
        saving_path,
        config_figure,
        fig_color=TEMP_CONFIG["color"],
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_wspace=TEMP_CONFIG["wspace"]
    )

def backend_temporal_trend(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq9_backend_temporal_trend.pdf",
):

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (4, 3),
        "legend_nlocal": 2
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        ["rq9_backend_type", "bib_year"], 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    saving_path: str

    # Parse the raw data
    backend_types = parse_column(req_data[0])
    years = req_data[1]
    sort_years = sorted(list(set(years)))
    sort_years = [int(temp_year) for temp_year in sort_years]   # Covert into int
    yearly_counts = {year: 0 for year in sort_years}
    type_freq =  {}

    for backend_type, year in zip(backend_types, years):
        if len(backend_type) == 0:  # Skip invalid data
            continue
        
        for meta_type in backend_type:
            yearly_counts[year] += 1
            if meta_type not in type_freq.keys():
                type_freq[meta_type] = {temp_year: 0 for temp_year in sort_years}
            type_freq[meta_type][year] += 1

    # Convert the frequencies ino required proportions
    type_prop = {}
    for meta_type, freq_dict in type_freq.items():
        if meta_type not in type_prop.keys():
            type_prop[meta_type] = []
        
        for temp_year in sort_years:
            if yearly_counts[temp_year] > 0:
                type_prop[meta_type].append(
                    freq_dict[temp_year] / yearly_counts[temp_year]
                )
            else:
                type_prop[meta_type].append(0)                
    

    bar_chart_general(
        sort_years,
        type_prop,
        {"x": "Year", "y": "Proportion of backends"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_offset=0.1,
        if_data=False,
        legend_nlocal=TEMP_CONFIG["legend_nlocal"]
        # fig_barwidth=TEMP_CONFIG["bar_height"],
        # fig_color=TEMP_CONFIG["color"],
        # rotation_angle=TEMP_CONFIG["angle"]
    )

def backend_output(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq9_backend_output.pdf",
):

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (8, 0.75),
        "annote_color": "black"
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq9_backend_output", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    saving_path: str

    # Parse the raw data
    backend_outputs = parse_column(req_data)
    output_types = {}
    for backend_output in backend_outputs:
        if len(backend_output) == 0:    # Skip the invalid data
            continue

        for meta_output in backend_output:
            if meta_output not in output_types.keys():
                output_types[meta_output] = 1
            else:
                output_types[meta_output] += 1

    backend_output_label = list(output_types.keys())
    backend_output_counts = [
        type_counts for type_counts in output_types.values()
    ]

    # Generate the plot
    horizontal_stacked_bar_chart(
        backend_output_counts,
        backend_output_label,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_anno_color=TEMP_CONFIG["annote_color"]
    )


if __name__ == "__main__":
    PROCEDURE = [
        ("fig", backend_types),
        ("fig", backend_temporal_trend),
        ("fig", backend_output)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data) # type: ignore

    print("\nRQ9 is done. \n")