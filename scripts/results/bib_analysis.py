"""
Code for the visualization of bibliometric analysis
"""

import pandas as pd
import os 
import re
from collections import Counter

from src import (
    read_csv, read_config_json, 
    line_chart_frequencies, pie_chart, horizontal_bar_chart, vertical_bar_chart,
    data_preprocess, data_clean
)
from scripts import (
    ROOT_DIR,
    FILE_NAME,
    FILE_DIR, 
    CONFIG_DATA_NAME, 
    CONFIG_FIGURE_NAME,
    FIG_SAVING_DIR
)

def year(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict, 
    saving_name: str = "bib_year.pdf"
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "offset": 0.7,              # Offset above the data point for the label
        "figsize": (3.5, 2.25),
        "ylim": [0, 25],            # y-axis display range
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "bib_year", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )
    
    saving_path: str
    line_chart_frequencies(
        req_data, 
        {"x": "Year", "y": "# of primary studies"}, 
        saving_path,
        config_figure,
        fig_offset=TEMP_CONFIG["offset"],
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_ylim=TEMP_CONFIG["ylim"]
    )

def venue_type(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict, 
    saving_name: str = "bib_venue_types.pdf"
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3, 3.5),
        "explode": None,
        "startangle": 90,
        "offset": 0.25,
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "bib_venue_type", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    # Extract terms within "[]"
    req_data = data_clean(req_data)    

    saving_path = os.path.join(ROOT_DIR, *FIG_SAVING_DIR, saving_name)
    pie_chart(
        req_data,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_explode=TEMP_CONFIG["explode"],
        fig_startangle=TEMP_CONFIG["startangle"],
        fig_offset=TEMP_CONFIG["offset"]       
    )    

def venue_name(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "bib_venue_names.pdf"
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3.8, 3.25),
        "bar_height": 0.25,
        "color": "#B7B5B7F8"
    }

    # Extract target data for analysis
    req_data, saving_path = data_preprocess(
        df, 
        "bib_venue_name", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    ) # type: ignore
    
    # Help to classify "Others"
    assist_data, _ = data_preprocess(
        df, 
        "bib_venue_type", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    

    # Extract terms within "[]"
    req_data = data_clean(req_data)  
    assist_data = data_clean(assist_data)  

    # Extract abbreviations if they exist
    for idx, meta_data in enumerate(req_data):
        match = re.search(r'\(([^()]*)\)', meta_data)  # Match the content in the first parentheses
        if match:
            req_data[idx] = match.group(1).strip()
        else:
            req_data[idx] = meta_data.strip() 

    # Change items with one occurrence to "Others" and delete ArXiv
    counts = Counter(req_data)  # Count the frequencies
    temp_list = []
    for req_item, assist_item in zip(req_data, assist_data):
        if req_item.lower() != "arxiv":
            if counts[req_item] == 1:
                temp_list.append(f"Other {assist_item[0].upper()}.")
            elif counts[req_item] > 1:
                temp_list.append(req_item)

    req_data = temp_list.copy()
    
    saving_path: str
    horizontal_bar_chart(
        req_data, 
        {"x": "# of primary studies", "y": "Venues"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barheight=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"]
    )


def se_problem(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "bib_se_problems.pdf"
) -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (2, 2.25),
        "bar_height": 0.25,
        "color": "#98ECF7F8"
    }

    # Extract target data for analysis
    req_data, saving_path = data_preprocess(
        df, 
        "SE_problem", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )   

    # Extract terms within "[]"
    req_data = data_clean(req_data)  
 
    vertical_bar_chart(
        req_data, 
        {"x": "SE problems", "y": "# of primary studies"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barwidth=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"]
    )

if __name__ == "__main__":
    PROCEDURE = [
        ("fig", year), 
        ("fig", venue_type),
        ("fig", venue_name),
        ("fig", se_problem)
    ]


    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure)

    print("\nBibliometric Analysis is done. \n")