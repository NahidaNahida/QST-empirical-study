"""
Code for the data analysis of RQ2 Buggy Objects
"""

from src import (
    read_csv, read_config_json,
    vertical_bar_chart, pie_chart, horizontal_boxplot, upset_plot, data_clean,
    vertical_tables, two_dimensional_table, two_dimensional_heatmap,
    parse_column, data_preprocess, number2camelform
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
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from itertools import product


def fault_generation_distribution(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq2_distribution_of_generation_approaches.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (2, 2.25),
        "bar_height": 0.25,
        "color": "#98ECF7F8"
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq2_generation_approaches", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    gen_approaches = parse_column(req_data, skip_invalid_value=False)
    collected_approaches = []
    for gen_approach in gen_approaches:
        if len(gen_approach) == 0:
            continue

        if isinstance(gen_approach, dict):
            collected_approaches.extend(gen_approach.keys())
        elif isinstance(gen_approach, list):
            collected_approaches.extend(gen_approach)

    vertical_bar_chart(
        collected_approaches, 
        {"x": "Approaches", "y": "# of primary studies"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barwidth=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"]
    )

def variant_distribution(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict, 
    saving_name: str = "rq2_variant_distribution.pdf"
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
        "rq2_buggy_numbers", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    

    variant_counts = parse_column(req_data, skip_invalid_value=False)

    variant_type_list = []
    num_of_studies = 0
    for variant_count in variant_counts:
        if len(variant_count) == 0:
            continue
        num_of_studies += 1
        variant_type_list.extend(list(variant_count.keys()))

    prop_of_studies = f"{num_of_studies / len(req_data) * 100:.1f}%"
    pie_chart(
        variant_type_list,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_explode=TEMP_CONFIG["explode"],
        fig_startangle=TEMP_CONFIG["startangle"],
        fig_offset=TEMP_CONFIG["offset"],
        title=f"Prop. of primary studies: {num_of_studies}/{len(req_data)} ({prop_of_studies})",       
    )        


def number_of_variants(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq2_variant_number" 
) -> None:

    TEMP_CONFIG = {
        "target_items": ["Mutant-level", "Version-level"],
        "figsize": (5, 0.55),
        "legendsize": (10, 1),
        "bar_height": 0.25,
        "color": "#69DAFFF8",
        "fig_median_offset" : (-2, 20),
        "fig_max_offset": (0, 4),
        "samplesize_name": None,
        "xinteger": {"Mutant-level": False, "Version-level": True},
        "no_ytick": True,
    }

    # Get the target data
    req_data, general_saving_path = data_preprocess(
        df, 
        "rq2_buggy_numbers",       
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )

    variant_counts = parse_column(req_data)

    variant_numbers = {target_item: [] for target_item in TEMP_CONFIG["target_items"]}

    legend_saved = False    # Whether the legend is saved
    for temp_target_item in variant_numbers.keys():
        saving_path = f"{general_saving_path}_{(temp_target_item.split())[0]}.pdf"
        for variant_count in variant_counts:
            if len(variant_count) == 0:
                continue
            if temp_target_item in variant_count.keys():
                variant_numbers[temp_target_item].extend(variant_count[temp_target_item])

        temp_list = np.array(variant_numbers[temp_target_item], dtype=int)
        horizontal_boxplot(
            [temp_list], 
            {"x": "# of buggy variants", "y": ""},
            saving_path,
            config_figure,
            samplesize_name=TEMP_CONFIG["samplesize_name"], fig_figsize=TEMP_CONFIG["figsize"],
            fig_color=TEMP_CONFIG["color"],fig_xinteger=TEMP_CONFIG["xinteger"][temp_target_item],
            no_ytick=TEMP_CONFIG["no_ytick"],fig_median_offset=TEMP_CONFIG["fig_median_offset"],
            fig_max_offset=TEMP_CONFIG["fig_max_offset"]
        )
        if not legend_saved:
            saving_path = f"{general_saving_path}_legend.pdf"
            horizontal_boxplot(
                [temp_list], {"x": "# of buggy variants", "y": ""}, saving_path, config_figure,
                samplesize_name=TEMP_CONFIG["samplesize_name"], fig_figsize=TEMP_CONFIG["legendsize"],
                fig_color=TEMP_CONFIG["color"],fig_xinteger=TEMP_CONFIG["xinteger"], 
                legend_only=True,fig_median_offset=TEMP_CONFIG["fig_median_offset"]
            )
            legend_saved = True

def sources_for_variants(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq2_sources_for_variants.tex"
) -> None:
    TEMP_CONFIG = {
        "target_items": ["Real-world bugs", "Imperfect models", "Mutation tooling"],
        "headers": ["Approaches", "Sources", "Primary studies", "\\#"],
        "cite_key": "", # "studied",
        "tab_space": (
            r">{\centering\arraybackslash}p{0.3\columnwidth} "
            r">{\centering\arraybackslash}p{0.3\columnwidth} "
            r"p{0.32\columnwidth} "
            r">{\centering\arraybackslash}p{0.05\columnwidth}"
        )
    }
 

    req_data, saving_path = data_preprocess(
        df, 
        ["rq2_generation_approaches", "primary_study_id"], 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )   

    variant_counts = parse_column(req_data[0])
    paper_ids = req_data[1]

    variant_sources = {
        target_item: []
        for target_item in TEMP_CONFIG["target_items"]
    }

    for paper_id, variant_count in zip(paper_ids, variant_counts):
        if len(variant_count) == 0:
            continue

        for approach, source in variant_count.items():
            if approach in variant_sources.keys():
                temp_list = variant_sources[approach]
            else:
                continue

            # Transverse the sources
            for meta_source in source:
                if len(temp_list) == 0:
                    temp_list.append({
                        "source": meta_source,
                        "paper_list": [f"\\Paper{number2camelform(int(paper_id))}"],
                        "paper_number": 1
                    })
                else:
                    if_existing = False
                    for temp_dict in temp_list:
                        if temp_dict["source"] == meta_source:
                            temp_dict["paper_list"].append(f"\\Paper{number2camelform(int(paper_id))}")
                            temp_dict["paper_number"] += 1
                            if_existing = True
                            break
                    if not if_existing:
                        temp_list.append({
                            "source": meta_source,
                            "paper_list": [f"\\Paper{number2camelform(int(paper_id))}"],
                            "paper_number": 1
                        })

    # Reformulate the data
    for approach_list in variant_sources.values():
        # Sort based on the number of papers
        approach_list.sort(
            key=lambda x: len(x.get("paper_list", [])),
            reverse=True        
        )

        for meta_dict in approach_list:
            target_list = meta_dict["paper_list"].copy()
            meta_dict["paper_list"] = (
                f"\\cite{TEMP_CONFIG['cite_key']}{{{', '.join(str(x) for x in target_list)}}}"
            )

    vertical_tables(
        variant_sources,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        if_cmidrule=True
    )


def mutation_operators(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict, 
    saving_name: str = "rq2_mutation_operators.pdf"
) -> None:
    TEMP_CONFIG = {
        "target_item": "Mutation operators",
        "desired_order": [
            "Gate",
            "Measurement",
            "Conditional",
            "Expression",
            "Variable",
            "Subroutine",
            "Branch",
        ],
        "figsize": (4, 2.5)
    }

    req_data, saving_path = data_preprocess(
        df, 
        "rq2_generation_approaches", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )   

    gen_approaches = parse_column(req_data)

    # Collect the sets of actions and objects
    # Transverse the list of data
    action_list, object_list = [], []
    for gen_approach in gen_approaches:
        if len(gen_approach) == 0 or TEMP_CONFIG["target_item"] not in gen_approach.keys():
            continue
        
        operators = gen_approach[TEMP_CONFIG["target_item"]]    # List of used mutation operators
        for operator in operators:
            op_str_list = operator.split()
            temp_act = (op_str_list[0]).capitalize()
            temp_obj = " ".join(str(x) for x in op_str_list[1:])
            temp_obj = temp_obj.capitalize()    

            action_list.append(temp_act)
            object_list.append(temp_obj)

    candidate_actions = list(set(action_list))
    candidate_objects = list(set(object_list))

    # Counts the number for each combination of actions and objects
    count_dict = {act: {obj: "" for obj in candidate_objects} for act in candidate_actions}

    # Transverse again
    for gen_approach in gen_approaches:
        if len(gen_approach) == 0 or TEMP_CONFIG["target_item"] not in gen_approach.keys():
            continue
        
        operators = gen_approach[TEMP_CONFIG["target_item"]]    # List of used mutation operators
        for operator in operators:
            op_str_list = operator.split()
            temp_act = (op_str_list[0]).capitalize()
            temp_obj = " ".join(str(x) for x in op_str_list[1:])
            temp_obj = temp_obj.capitalize()   # Capitalize the first letter
            if count_dict[temp_act][temp_obj] == "":
                count_dict[temp_act][temp_obj] = "1"
            elif isinstance(count_dict[temp_act][temp_obj], str):
                count_dict[temp_act][temp_obj] = str(
                    int(count_dict[temp_act][temp_obj]) + 1
                )

    two_dimensional_heatmap(
        count_dict,
        {"x": "Targets", "y": "Actions"},
        TEMP_CONFIG["desired_order"],
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
    )
 

if __name__ == "__main__":
    PROCEDURE = [
        ("fig", fault_generation_distribution),
        ("fig", variant_distribution),
        ("fig", number_of_variants),
        ("tab", sources_for_variants),
        ("fig", mutation_operators)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)

    print("\nRQ2 is done. \n")