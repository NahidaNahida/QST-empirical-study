"""
Code for the data analysis of RQ1 Quantum Programs
"""

from src import (
    read_csv, read_config_json,
    line_chart_frequencies, pie_chart, horizontal_bar_chart, horizontal_boxplot,
    vertical_tables,
    parse_column, data_preprocess, paperids2citation
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

def algorithm_and_subroutine_names(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    data_keywords: list = ["Quantum algorithms and subroutines"],
    saving_name: str = "rq1_program_names.pdf"
) -> None:
    """
    Display the names of quantum algorithms and subroutines along with the frequencies
    """
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (4.5, 6),
        "bar_height": 0.25,
        "color": "#FFFCCEF8"
    }
    
    # Get the target data
    data, saving_path = data_preprocess(
        df, 
        "rq1_program_names",         
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    ) # type: ignore
    data: list
    saving_path: str
    # Extract the required term
    req_data: list[dict] = parse_column(data)
    # Removed the empity dictionary
    req_data = [elem for elem in req_data if elem != {}]

    req_metadata = {}
    for data_dict in req_data:
        if not isinstance(data_dict, dict):
            continue
        for data_keyword in data_keywords:
            if data_keyword in data_dict.keys():
                if data_keyword not in req_metadata.keys():  # Create a new key-value pair
                    req_metadata[data_keyword] = data_dict[data_keyword].copy()
                else:
                    req_metadata[data_keyword].extend(data_dict[data_keyword]) 

    # Mark algorithms with one sample as "Others"
    algorithm_counts = len(set(req_metadata[data_keywords[0]]))
    counts = Counter(req_metadata[data_keywords[0]])  # Count the frequencies
    updated_req_metadata = []
    for temp_data in req_metadata[data_keywords[0]]:
        if counts[temp_data] == 1:
            updated_req_metadata.append("Others")
        elif counts[temp_data] > 1:
            updated_req_metadata.append(temp_data)

    horizontal_bar_chart(
        updated_req_metadata, 
        {"x": "# of primary studies", "y": "Quantum algorithms and subroutines"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barheight=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"],
        title=f"# of quanutm algorithms or subroutines = {int(algorithm_counts)}" 
    )
    
def learning_models_names(
    df: pd.DataFrame,
    config_data: dict, 
    data_keywords: list = ["Quantum learning-based models"],
    saving_name: str = "rq1_learning_models_names.tex"
) -> None:
    TEMP_CONFIG = {
        "headers": ["Quantum learning-based models", "Primary studies", "\\#"],
        "tab_space": "p{{0.7\\columnwidth}}  p{{0.2\\columnwidth}} c"
    }

    # Get the target data
    data, saving_path = data_preprocess(
        df, 
        "rq1_program_names",         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    ) # type: ignore

    paper_ids, _  = data_preprocess(
        df, 
        "primary_study_id",         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )

    data: list
    saving_path: str
    # Extract the required term
    req_data: list[dict] = parse_column(data)
    req_metadata = {}
    for id, data_dict in zip(paper_ids, req_data):
        if data_dict == {}:
            continue
        # Filter the data out of the keyword list
        for data_keyword in data_keywords:
            if not isinstance(data_dict, dict):
                continue
            if data_keyword in data_dict.keys():
                if data_keyword not in req_metadata.keys(): # Create a dict for each keyword
                    req_metadata[data_keyword] = {}
                
                for meta_model in data_dict[data_keyword]:
                    if meta_model not in req_metadata[data_keyword].keys():
                        # Initialize data for each learning-based model
                        req_metadata[data_keyword][meta_model] = {
                            "paper_ids": [],
                            "paper_numbers": 0
                        }
                    
                    req_metadata[data_keyword][meta_model]["paper_ids"].append(id)
                    req_metadata[data_keyword][meta_model]["paper_numbers"] += 1
                
    # Reformulate the data frame
    for meta_model, meta_data in req_metadata[data_keywords[0]].items():
        # Paper numbers: int -> str
        meta_data["paper_numbers"] = str(meta_data["paper_numbers"])
        # Paper citation
        meta_data["paper_ids"] = paperids2citation(meta_data["paper_ids"])

    # Sort by paper_numbers from largest to smallest
    # First, make sure paper_numbers is an int
    sorted_metadata = dict(
        sorted(
            req_metadata[data_keywords[0]].items(),
            key=lambda item: int(item[1]["paper_numbers"]),
            reverse=True
        )
    )

    # Generate latex table
    vertical_tables(sorted_metadata, TEMP_CONFIG["headers"], saving_path, TEMP_CONFIG["tab_space"])

def number_of_objects(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq1_object_numbers" # For the following "rq1_object_numbers_{}.pdf"
) -> None:
    """
    Display the boxplots of the object numbers for each type of programs
    """
    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (3.5, 0.75),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color": "#FFFDCEF8",
        "samplesize_name": "# of primary studies",
        "xinteger": True,
        "no_ytick": True,
    }
    
    # Get the target data
    data, saving_path = data_preprocess(
        df, 
        "rq1_object_numbers",         
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    ) # type: ignore

    data: list
    saving_path: str
    # Extract the required term
    req_data: list[dict[str, list]] = parse_column(data)
    req_data = [elem for elem in req_data if elem != {}]
    program_numbers_dict = {}
    for paper_data in req_data:
        for paper_data_type, paper_data_number in paper_data.items():
            paper_data_number = [int(temp_number) for temp_number in paper_data_number]
            if paper_data_type not in program_numbers_dict.keys():
                program_numbers_dict[paper_data_type] = paper_data_number.copy()
            else:
                program_numbers_dict[paper_data_type].extend(paper_data_number)
    
    legend_saved = False    # Whether the legend is saved
    for program_type, program_numbers in program_numbers_dict.items():
        specific_str = ("_".join(program_type.split()[:2])).lower()
        temp_data: np.ndarray = np.array(program_numbers)
        temp_saving_path = f"{saving_path}_{specific_str}.pdf"
        horizontal_boxplot(
            [temp_data], {"x": "# of objects", "y": ""}, temp_saving_path, config_figure,
            samplesize_name=TEMP_CONFIG["samplesize_name"], fig_figsize=TEMP_CONFIG["figsize"],
            fig_color=TEMP_CONFIG["color"],fig_xinteger=TEMP_CONFIG["xinteger"],
            no_ytick=TEMP_CONFIG["no_ytick"]
        )
        if not legend_saved:
            temp_saving_path = f"{saving_path}_legend.pdf"
            horizontal_boxplot(
                [temp_data], {"x": "# of objects", "y": ""}, temp_saving_path, config_figure,
                samplesize_name=TEMP_CONFIG["samplesize_name"], fig_figsize=TEMP_CONFIG["legendsize"],
                fig_color=TEMP_CONFIG["color"],fig_xinteger=TEMP_CONFIG["xinteger"], 
                legend_only=True
            )
            legend_saved = True
    


if __name__ == "__main__":
    PROCEDURE = [
        ("fig", algorithm_and_subroutine_names),
        ("fig", number_of_objects),
        ("tab", learning_models_names),
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)

    print("\nRQ1 is done. \n")