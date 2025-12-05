"""
Code for the data analysis of RQ7 Contrastive Analysis
"""

from src import (
    read_csv, read_config_json,
    line_chart_frequencies, pie_chart, horizontal_bar_chart, vertical_bar_chart, data_clean,
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
from collections import OrderedDict

import warnings
warnings.filterwarnings("ignore")

BASELINE_ORDER = ["SOTA", "Ablation",  "Adaption", "Composite", "Naivety"]

def baseline_numbers(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq7_number_of_baselines.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "if_sort": False,  # Sort based on the frequencies, otherwise the baseline order
        "figsize": (3, 2),
        "bar_height": 0.25,
        "color": "#FFFCCEF8"
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq7_baseline_names", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    # Extract terms within "[]"
    req_data = parse_column(req_data)
    baseline_numbers = [len(meta_data) for meta_data in req_data]
 
    req_baseline_order = None if TEMP_CONFIG["if_sort"] else BASELINE_ORDER

    horizontal_bar_chart(
        baseline_numbers, 
        {"x": "# of primary studies", "y": "# of baselines"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barheight=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"]
    )

def baseline_motivations(
    df: pd.DataFrame,
    config_data: dict, 
    config_figure: dict,  
    saving_name: str = "rq7_inclusion_motivation.pdf",
) -> None:

    # Instant configuration
    TEMP_CONFIG = {
        "if_sort": False,  # Sort based on the frequencies, otherwise the baseline order
        "figsize": (2.2, 1.85),
        "bar_height": 0.25,
        "color": "#B7B5B7F8"
    }
    
    req_data, saving_path = data_preprocess(
        df, 
        "rq7_baseline_motivation", 
        config_data, 
        ROOT_DIR, 
        FIG_SAVING_DIR,
        saving_name
    )    
    
    # Extract terms within "[]"
    req_data = parse_column(req_data)
    category_counts = []
    for paper_data in req_data:
        if len(paper_data) == 0:  # Skip invalid data
            continue
        paper_data: list[str]
        category_counts.extend([meta_data for meta_data in paper_data])


    req_baseline_order = None if TEMP_CONFIG["if_sort"] else BASELINE_ORDER


    vertical_bar_chart(
        category_counts, 
        {"x": "Categories of baselines", "y": "# of baselines"}, 
        saving_path,
        config_figure,
        fig_figsize=TEMP_CONFIG["figsize"],
        fig_barwidth=TEMP_CONFIG["bar_height"],
        fig_color=TEMP_CONFIG["color"],
        if_freq_sort=TEMP_CONFIG["if_sort"],
        req_sort=req_baseline_order
    )

def baseline_names(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq7_baseline_names.tex",
):
    """
    For the following code, we skip "Ablation study", as this kind of baseline 
    is proposed artificially and hardly adapted to other studies.
    """

    TEMP_CONFIG = {
        "if_sort": False,  # Sort based on the frequencies, otherwise the baseline order
        "headers": ["SE problems", "Categories", "Baselines (Correspondings primary studies)"], 
        "tab_space": "p{0.15\\columnwidth}  c  p{0.7\\columnwidth}",
        "skip_category": "Ablation"
    }

    multi_data, saving_path = data_preprocess(
        df, 
        [
            "rq7_baseline_names", "rq7_baseline_motivation",
            "primary_study_id", "SE_problem"
        ], 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )    

    baseline_names = parse_column(multi_data[0])
    baseline_categories = parse_column(multi_data[1])
    paper_idxes = multi_data[2]
    se_problems = parse_column(multi_data[3])

    # Determine all possible baseline categories
    category_counts = []
    for paper_data in baseline_categories:
        if paper_data:  # skip empty
            category_counts.extend(paper_data)
    category_set = list(set(category_counts))

    # Build data structure
    req_data = {}
    for baseline_name, baseline_category, paper_idx, se_problem_list in zip(
        baseline_names, baseline_categories, paper_idxes, se_problems
    ):
        if not baseline_name:
            continue

        se_problem = se_problem_list[0]

        # Initialize SE problem entry
        if se_problem not in req_data:
            req_data[se_problem] = [
                {temp_category: []} for temp_category in category_set
            ]

        # Fill data
        for baseline_indx, single_baseline in enumerate(baseline_name):
            category = baseline_category[baseline_indx]
            for cata_dict in req_data[se_problem]:
                if category in cata_dict:
                    name_list = cata_dict[category]
                    break
            else:
                continue  # category not found

            # Append or update paper references
            paper_tag = f"\\Paper{number2camelform(int(paper_idx))}"
            for temp_dict in name_list:
                if single_baseline in temp_dict:
                    temp_dict[single_baseline].append(paper_tag)
                    break
            else:
                name_list.append({single_baseline: [paper_tag]})

    # --------------------------------------------------------------------------
    # Reformulate & sort baselines
    # --------------------------------------------------------------------------
    for se_problem, baseline_list in req_data.items():
        for baseline_dict in baseline_list:
            # 1. Remove "Ablation"
            baseline_dict.pop(TEMP_CONFIG["skip_category"], None)

            # 2. Remove empty entries
            empty_keys = [k for k, v in baseline_dict.items() if not v]
            for k in empty_keys:
                del baseline_dict[k]

            # 3. Sort & format (use list() to avoid RuntimeError)
            new_entries = {}
            for baseline_category, baseline_name_list in list(baseline_dict.items()):
                if not isinstance(baseline_name_list, list):
                    continue

                # Sort by citation frequency
                baseline_name_list.sort(
                    key=lambda d: len(next(iter(d.values()), [])),
                    reverse=True
                )

                # Format baseline string
                formatted = ", ".join(
                    f"""{list(temp_dict.keys())[0]} (\\cite{{{", ".join(list(temp_dict.values())[0])}}})"""
                    for temp_dict in baseline_name_list
                )

                # Save both raw and formatted
                new_entries[baseline_category] = baseline_name_list
                new_entries[f"{baseline_category}_formatted"] = formatted

            # Replace original dict
            baseline_dict.clear()
            baseline_dict.update(new_entries)

 
        if TEMP_CONFIG["if_sort"]:
            # 对同一 se_problem 下的 category 列表按该 category 的 baseline 总数降序排序，
            # 以便 baselines 数量大的 category 排在前面。
            baseline_list.sort(
                key=lambda d: sum(
                    len(v) for k, v in d.items()
                    if (not k.endswith("_formatted")) and isinstance(v, list)
                ),
                reverse=True
            )
        else:
            # 按 BASELINE_ORDER 顺序排序，未出现的元素排在后面，保持原相对顺序
            baseline_order_index = {name: i for i, name in enumerate(BASELINE_ORDER)}
            
            baseline_list.sort(
                key=lambda d: min(
                    (baseline_order_index[k] for k in d if k in baseline_order_index),
                    default=len(BASELINE_ORDER)
                )
            )

        # Clean up empty baseline dicts
        req_data[se_problem] = [d for d in baseline_list if d]


    # --------------------------------------------------------------------------
    # Transform to LaTeX table-friendly format + Build summary_dict
    # --------------------------------------------------------------------------
    summary_dict = {}

    for se_problem, baseline_list in req_data.items():
        new_list = []
        category_count_map = {}  # 记录各类 baseline 频数

        for baseline_dict in baseline_list:
            for category, baseline in baseline_dict.items():
                if category.endswith("_formatted"):  # only include formatted entries
                    clean_category = category.replace("_formatted", "")

                    # baseline 为字符串，因此需要得到原 baseline 个数
                    # baseline_dict 内部的同名非-formatted key是列表，长度就是数量
                    raw_list = baseline_dict.get(clean_category, [])
                    count = len(raw_list)

                    # 记录计数
                    if count > 0:
                        category_count_map[clean_category] = count

                    # 保存给 req_data 用（LaTeX）
                    new_list.append({
                        "category": clean_category,
                        "baseline": baseline
                    })

        # 替换回 req_data
        req_data[se_problem] = new_list

        # -------------------------
        # Build summary entry
        # -------------------------
        total_count = sum(category_count_map.values())
        category_parts = [
            f"{cata} ({num})" for cata, num in category_count_map.items() if num > 0
        ]
        summary_dict[f"{se_problem} ({total_count})"] = ", ".join(category_parts)

    additional_line = "\\newline\n    ".join(f"{key}: {val}" for key, val in summary_dict.items())
    additional_line = f"\\textbf{{Number of deduplicated baselines:}} \\newline\n    {additional_line}"
    additional_line = f"\\multicolumn{{{len(TEMP_CONFIG['headers'])}}}{{p{{\\columnwidth}}}}{{{additional_line}}}\\\\"
    additional_line = f"\\cmidrule(lr){{1-{len(TEMP_CONFIG['headers'])}}}\n{additional_line}"
    # --------------------------------------------------------------------------
    # Generate LaTeX table
    # --------------------------------------------------------------------------
    vertical_tables(
        req_data,
        TEMP_CONFIG["headers"],
        saving_path,
        TEMP_CONFIG["tab_space"],
        if_cmidrule=True,
        addition_line=additional_line
    )
 
 
def statistical_tests_for_comparison(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq7_baseline_comparison.tex",
):
    """
    For the following code, we skip "Ablation study", as the kind of baseline is proposed artificially and 
    hardly adapted to other studies.
    """

    TEMP_CONFIG = {
        "headers": ["Statistical tests (\#)", "Associated statistics (\#)"], 
        "tab_space": "p{0.5\columnwidth}  p{0.48\columnwidth}"
    }

    data, saving_path = data_preprocess(
        df, 
        "rq7_baseline_comparison", 
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )    

    # Parse the raw data
    comparison_methods = parse_column(data)

    # Record the Statistical tests and Statistics
    statistics_data = {}
    num_of_tests = {}
    total_num_of_studies = 0
    for comparison_method in comparison_methods:
        if len(comparison_method) == 0:     # Skip invalid data
            continue
        
        total_num_of_studies += 1
        for statistical_tests, statistics_list in comparison_method.items():
            if statistical_tests not in statistics_data.keys():
                statistics_data[statistical_tests] = {}  
            
            if statistical_tests not in num_of_tests.keys():
                num_of_tests[statistical_tests] = 1
            else:
                num_of_tests[statistical_tests] += 1

            for statistics in statistics_list:
                temp_dict = statistics_data[statistical_tests]
                if statistics not in temp_dict.keys():
                    temp_dict[statistics] = 1       # {stat: freq}
                else:
                    temp_dict[statistics] += 1

    # Reformulate the data
    final_req_data = statistics_data.copy()
    for statistical_tests, statistics_dict in statistics_data.items():
        stat_list = [
            f"{statistics} ({frequencies})"
            for statistics, frequencies in statistics_dict.items()
        ]
        
        stat_str = ", ".join(str(x) for x in stat_list)
        final_req_data[statistical_tests] = {"stat_str": stat_str}

    # Change the key, including the frequencies
    new_req_data = OrderedDict()
    for raw_key, data_str in final_req_data.items():
        new_req_data[f"{raw_key} ({num_of_tests[raw_key]})"] = data_str

    additional_line = f"\\textbf{{Total number of primary studies:}} {total_num_of_studies}"
    additional_line = f"    \\multicolumn{{{len(TEMP_CONFIG['headers'])}}}{{p{{\\columnwidth}}}}{{{additional_line}}}\\\\"
    additional_line = f"\\cmidrule(lr){{1-{len(TEMP_CONFIG['headers'])}}}\n{additional_line}"

    # Generate latex table
    vertical_tables(new_req_data, TEMP_CONFIG["headers"], saving_path, TEMP_CONFIG["tab_space"], addition_line=additional_line)

if __name__ == "__main__":
    PROCEDURE = [
        ("fig", baseline_numbers),
        ("fig", baseline_motivations),
        ("tab", baseline_names),
        ("tab", statistical_tests_for_comparison)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)

    print("\nrq7 is done. \n")