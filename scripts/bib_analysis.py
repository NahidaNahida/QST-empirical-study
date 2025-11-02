import pandas as pd
import os 
import re
from collections import Counter

from src import read_csv, read_config_json, line_chart, pie_chart, horizontal_bar_chart
from scripts import (
    ROOT_DIR,
    FILE_NAME,
    FILE_DIR, 
    CONFIG_DATA_NAME, 
    CONFIG_FIGURE_NAME,
    SAVING_DIR
)

def data_clean(data: list[str]) -> list[str]:
    clean_data = [item.replace("[", "").replace("]", "") for item in data]
    return clean_data

def data_preprocess(
    df: pd.DataFrame, 
    header_item: str, 
    config_data: dict, 
    saving_name: str
) -> tuple[list, str]:
    header = config_data["headers"][header_item]
    req_data = df[header].tolist()
    saving_path = os.path.join(ROOT_DIR, *SAVING_DIR, saving_name)
    return req_data, saving_path

def year(df, config_data, config_figure, saving_name: str = "bib_year.pdf") -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "offset": 0.7,              # Offset above the data point for the label
        "figsize": (3.5, 2.25),
        "ylim": [0, 25],            # y-axis display range
    }
    
    req_data, saving_path = data_preprocess(df, "bib_year", config_data, saving_name)
    line_chart(
        req_data, 
        {"x": "Year", "y": "# of primary studies"}, 
        saving_path,
        config_figure,
        temporal_config=TEMP_CONFIG
    )

def venue_type(df, config_data, config_figure, saving_name: str = "bib_venue_types.pdf") -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3, 3),
        "explode": None,
        "autopct": "%1.1f%%",
        "startangle": 90,
        "offset": 0.25,
    }
    
    req_data, saving_path = data_preprocess(df, "bib_venue_type", config_data, saving_name)    
    
    # Extract terms within "[]"
    req_data = data_clean(req_data)    

    saving_path = os.path.join(ROOT_DIR, *SAVING_DIR, saving_name)
    pie_chart(
        req_data,
        saving_path,
        config_figure,
        temporal_config=TEMP_CONFIG
    )    

def venue_name(df, config_data, config_figure, saving_name: str = "bib_venue_names.pdf") -> None:
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (5, 2),
        "bar_height": 0.25,
        "color": "#B7B5B7F8"
    }

    req_data, saving_path = data_preprocess(df, "bib_venue_name", config_data, saving_name)

    # Extract terms within "[]"
    req_data = data_clean(req_data)  

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
    for item in req_data:
        if item.lower() != "arxiv":
            if counts[item] == 1:
                temp_list.append("Others")
            elif counts[item] > 1:
                temp_list.append(item)
    req_data = temp_list.copy()
 
    horizontal_bar_chart(
        req_data, 
        {"x": "# of primary studies", "y": "Venues"}, 
        saving_path,
        config_figure,
        temporal_config=TEMP_CONFIG
    )
    
if __name__ == "__main__":
    PROCEDURE = [
        year, 
        venue_type,
        venue_name
    ]


    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for sub_proc in PROCEDURE:
        sub_proc(df, config_data, config_figure)

