"""
Code for the data analysis of RQ6 Evaluation Metrics
"""

from src import (
    read_csv, read_config_json,
    two_labels_venn, upset_plot,
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


def top_k_with_ties(sorted_list, k):
    """
    sorted_list: 已按目标值降序排序的列表，如 [(metric, [paper_ids]), ...]
    k: 希望至少保留的前 k 项，但会继续保留并列的项

    返回：保留并列后的列表
    """
    if not isinstance(k, int) or k <= 0 or len(sorted_list) <= k:
        return sorted_list

    # 第 k 个元素的 count
    kth_count = len(sorted_list[k - 1][1])

    # 保留所有 count >= kth_count
    return [
        item for item in sorted_list
        if len(item[1]) >= kth_count
    ]

def whether_reporting_metrics(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq6_metrics_venn.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "figsize": (4, 2),
        "annote_color": "black",
        "ellipse": 1.15,  # Eccentricity of the ellipse
        "offset": {"A": (0.2, 0),"B": (0.2, 0.05), "01": (0.08, 0)}
    }
    
    multi_data, saving_path = data_preprocess(
        df, 
        ["rq6_effectiveness", "rq6_cost"], 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    

    effect_metrics = parse_column(multi_data[0])
    cost_metrics = parse_column(multi_data[1])    
 
    counts_dict = {"Effectiveness": 0, "Cost": 0, "Intersection": 0}
    
    for effect_metric, cost_metric in zip(effect_metrics, cost_metrics):
        if len(effect_metric) == 0 and len(cost_metric) > 0:
            counts_dict["Cost"] += 1
        elif len(effect_metric) > 0 and len(cost_metric) == 0:
            counts_dict["Effectiveness"] += 1
        elif len(effect_metric) > 0 and len(cost_metric) > 0:
            counts_dict["Intersection"] += 1
    

    counts_tuple = tuple(counts_dict.values())
    labels_tuple = tuple(list(counts_dict.keys())[:2])

    two_labels_venn(
        counts_tuple, 
        labels_tuple,
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        ellipse=TEMP_CONFIG["ellipse"],
        label_offset=TEMP_CONFIG["offset"]
    )

def metrics_table(
    df: pd.DataFrame,
    config_data: dict,
    saving_name: str = "rq6_metrics_names.tex",     
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "headers": ["SE problems", "Effectiveness (\\#)", "Cost (\\#)"],
        "tab_space": "c  p{0.46\\columnwidth} p{0.38\\columnwidth}",
        "if_top_k": 5,
        "if_only_numbers": True
    }

    multi_data, saving_path = data_preprocess(
        df, 
        ["rq6_effectiveness", "rq6_cost", "primary_study_id", "bib_SE_problem"], 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )    


    effect_metrics = parse_column(multi_data[0])
    cost_metrics = parse_column(multi_data[1])
    paper_idxes = multi_data[2]
    se_problems = parse_column(multi_data[3])
 
    # Build data structure
    final_metric_names = {}
    for effect_metric, cost_metric, paper_idx, se_problem_list in zip(
        effect_metrics, cost_metrics, paper_idxes, se_problems
    ):
        if len(effect_metric) == 0 and len(cost_metric) == 0:
            continue

        se_problem = se_problem_list[0]

        # Initialize SE problem entry
        if se_problem not in final_metric_names.keys():
            final_metric_names[se_problem] = {"Effectiveness": {}, "Cost": {}}

        # Check the effectiveness
        effect_dict = final_metric_names[se_problem]["Effectiveness"]
        for meta_effect in effect_metric:
            if meta_effect not in effect_dict.keys():
                effect_dict[meta_effect] = [f"\\Paper{number2camelform(int(paper_idx))}"]
            else:
                effect_dict[meta_effect].append(f"\\Paper{number2camelform(int(paper_idx))}")

        # Check the cost
        cost_dict = final_metric_names[se_problem]["Cost"]
        for meta_cost in cost_metric:
            if meta_cost not in cost_dict.keys():
                cost_dict[meta_cost] = [f"\\Paper{number2camelform(int(paper_idx))}"]
            else:
                cost_dict[meta_cost].append(f"\\Paper{number2camelform(int(paper_idx))}") 

    for se_problem, metric_dict in final_metric_names.items():
        new_metric_dict = {}
        for metric_type, meta_metric_data in metric_dict.items():

            # 排序：根据出现次数（list 长度）降序
            sorted_meta_metric_data = sorted(
                meta_metric_data.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )

            # ====== 新增功能：保留 top-k ======
            top_k = TEMP_CONFIG.get("if_top_k", None)
            if isinstance(top_k, int) and top_k > 0:
                sorted_meta_metric_data = top_k_with_ties(sorted_meta_metric_data, top_k)
            # =================================

            final_data_list = []
            for metric_name, paper_id_list in sorted_meta_metric_data:
                if TEMP_CONFIG["if_only_numbers"]:      # Only display the number of primary studies
                    paper_str = str(len(paper_id_list))
                else:
                    paper_str = f"""\\cite{{{', '.join(str(x) for x in paper_id_list)}}}"""
                final_data_list.append(f"{metric_name} ({paper_str})")

            new_metric_dict[metric_type] = ",\\newline ".join(final_data_list)
            new_metric_dict[metric_type] = f"{new_metric_dict[metric_type]}."

        metric_dict.clear()
        metric_dict.update(new_metric_dict)
        


    vertical_tables(
        final_metric_names,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        if_midrule_each_line=True
    )


if __name__ == "__main__":
    PROCEDURE = [
        ("fig", whether_reporting_metrics),
        ("tab", metrics_table),
        # ("tab", input_type_name)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data) # type: ignore

    print("\nrq6 is done. \n")