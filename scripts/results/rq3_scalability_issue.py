"""
Code for the data analysis of RQ1 Quantum Programs
"""

from src import (
    read_csv, read_config_json,
    line_chart, pie_chart, horizontal_bar_chart, horizontal_boxplot, upset_plot, data_clean,
    vertical_tables,
    parse_column, data_preprocess, paperids2citation, get_min_max, dict2upsetform
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

def whether_scalability(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq3_whether_scalability.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (2.8, 2.8),
        "explode": None,
        "startangle": 90,
        "offset": 0.25,
        "max_point_offset": (0, 4)
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq3_whether_scalability", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    # Extract terms within "[]"
    req_data = data_clean(req_data)    
    # Replace "Y" to "Yes" and "N" to "No"
    renamed_data = []
    for meta_data in req_data:
        if meta_data.lower() == "y":
            renamed_data.append("Yes")
        elif meta_data.lower() == "n":
            renamed_data.append("No")

    saving_path = os.path.join(ROOT_DIR, *FIG_SAVING_DIR, saving_name)
    pie_chart(
        renamed_data,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_explode=TEMP_CONFIG["explode"],
        fig_startangle=TEMP_CONFIG["startangle"],
        fig_offset=TEMP_CONFIG["offset"]       
    )    


def circuit_complexity(    
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name_upset: str = "rq3_scalability_upsetplot.pdf",
    saving_name_numbers: str = "rq3_scalability"  # For the following "rq3_scalability_{}.pdf"
) -> None:
    """
    Display the names of quantum algorithms and subroutines along with the frequencies
    """
    # Instant configuration
    TEMP_CONFIG_UPSET = {
        "figsize": (3.5, 2.5),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color": "black",
        "wspace": -0.45
    }
    
    TEMP_CONFIG_BOX = {
        "figsize": (3.5, 0.55),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color":{"min": "#69DAFFF8", "max": "yellow"},
        "fig_median_offset" : (-2, 20),
        "fig_max_offset": (0, 4),
        "samplesize_name": None,
        "xinteger": True,
        "no_ytick": True,
    }

    # Get the target data
    multi_data, saving_paths = data_preprocess(
        df, 
        ["rq3_qubits", "rq3_gates", "rq3_depth"],         
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        [saving_name_upset, saving_name_numbers]
    ) # type: ignore
    multi_data: list[list]
    saving_paths: list[str]

    number_data = {}

    req_terms = ["Qubit", "Gate","Depth" ]      # Do not change their names
    parsed_data_dict = {
        complex_name: parse_column(data)      # Data: including {}
        for complex_name, data in zip (req_terms, multi_data) 
    }

    data_size = len(parsed_data_dict[req_terms[0]])
    for data_idx in range(data_size):
        # Calculate the maxinum and minimum
        # For "Qubit" and "Depth", the metadata are only lists.
        # For "Gate", we merely consider the total numbers
        for req_term in req_terms:
            paper_data = parsed_data_dict[req_term][data_idx]
            
            if len(paper_data) == 0:  # Skip {}
                continue
 
            if req_term != "Gate":             # For the list[str] in "Qubit" and "Depth"
                min_num, max_num = get_min_max(paper_data)
            else:                               # For the list[dict] in "Gate"
                temp_req_data = []
                if "Total" in paper_data.keys():
                    temp_req_data.extend(paper_data["Total"])
                else:
                    continue
                min_num, max_num = get_min_max(temp_req_data)
            if req_term not in number_data.keys():
                number_data[req_term] = {"max": [max_num], "min": [min_num]}
            else:
                number_data[req_term]["max"].append(max_num)
                number_data[req_term]["min"].append(min_num)
            
    # Analyse the upset relation
    combo_list, count_list = dict2upsetform(parsed_data_dict)    
 
    # Generate the upset plot
    upset_plot(
        {"memberships": combo_list, "values": count_list}, 
        # {"x": "# of primary studies", "y": "# of intersaction"},
        saving_paths[0],
        config_figure,
        fig_color=TEMP_CONFIG_UPSET["color"],
        fig_figsize=TEMP_CONFIG_UPSET["figsize"],
        fig_wspace=TEMP_CONFIG_UPSET["wspace"]
    )

    # Generate boxplots by order
    x_legend = {
        req_terms[0]: "# of qubits", req_terms[1]: "# of gates", req_terms[2]: "Depths"
    }
    legend_saved = False    # Whether the legend is saved
    for req_term, temp_dict in number_data.items():
        for data_name, temp_list in temp_dict.items():
            temp_list = np.array(temp_list)
            final_saving_path = f"{saving_paths[1]}_{req_term}_{data_name}.pdf"
            horizontal_boxplot(
                [temp_list], 
                {"x": x_legend[req_term], "y": ""},
                final_saving_path,
                config_figure,
                samplesize_name=TEMP_CONFIG_BOX["samplesize_name"], fig_figsize=TEMP_CONFIG_BOX["figsize"],
                fig_color=TEMP_CONFIG_BOX["color"][data_name],fig_xinteger=TEMP_CONFIG_BOX["xinteger"],
                no_ytick=TEMP_CONFIG_BOX["no_ytick"],fig_median_offset=TEMP_CONFIG_BOX["fig_median_offset"],
                fig_max_offset=TEMP_CONFIG_BOX["fig_max_offset"]
            )
            if not legend_saved:
                temp_saving_path = f"{saving_paths[1]}_legend.pdf"
                horizontal_boxplot(
                    [temp_list], {"x": "# of objects", "y": ""}, temp_saving_path, config_figure,
                    samplesize_name=TEMP_CONFIG_BOX["samplesize_name"], fig_figsize=TEMP_CONFIG_BOX["legendsize"],
                    fig_color=TEMP_CONFIG_BOX["color"][data_name],fig_xinteger=TEMP_CONFIG_BOX["xinteger"], 
                    legend_only=True,fig_median_offset=TEMP_CONFIG_BOX["fig_median_offset"]
                )
                legend_saved = True

if __name__ == "__main__":
    PROCEDURE = [
        ("fig", whether_scalability),
        ("fig", circuit_complexity)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        # elif type == "tab":
        #     sub_proc(df, config_data)

    print("\nRQ3 is done. \n")