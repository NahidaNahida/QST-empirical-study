"""
Code for the data analysis of RQ10 Available Toolings
"""

from src import (
    read_csv, read_config_json, data_clean, number2camelform,
    line_chart_frequencies, pie_chart, horizontal_bar_chart, horizontal_boxplot,
    vertical_tables, vertical_grouped_table,
    parse_column, data_preprocess, paperids2citation
)

 
from scripts import (
    ROOT_DIR,
    FILE_NAME,
    FILE_DIR, 
    CONFIG_DATA_NAME, 
    CONFIG_FIGURE_NAME,
    FIG_SAVING_DIR,
    TAB_SAVING_DIR,
    BIB_SAVING_DIR
)


import pandas as pd
from collections import Counter
import numpy as np
import bibtexparser
import os 
    
def available_sources(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq10_available_program_sources.tex",
    new_bib_name: str = "program_sources.bib"
) -> None:
    TEMP_CONFIG = {
        "headers": ["Program sources", "Repository links", "Primary studies", "\\#"],
        "tab_space": "p{{0.34\\columnwidth}}  p{{0.4\\columnwidth}} p{{0.215\\columnwidth}} c"
    }

    # Get the target data
    data, saving_path = data_preprocess(
        df, 
        "rq10_program_sources",         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    ) # type: ignore
    saving_path: str

    paper_ids, _  = data_preprocess(
        df, 
        "primary_study_id",         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    )

    # Extract the required term
    req_data: list[dict] = parse_column(data)  # Keep "Un-specified" in the raw data
    req_metadata = {}
    new_bibtex = []  # For generate the .bib for the program sources
    for paper_id, data_dict in zip(paper_ids, req_data):
        if data_dict == {}:
            continue

        for source_name, meta_data in data_dict.items():
            bibtex_str = data_clean([meta_data[0]], mode="outer")[0]     # Remove the outer "[" and "]"
            url_link = meta_data[1]
            
            # Process on the bibTex
            if bibtex_str.lower() != "un-specified":
                new_bibtex.append(bibtex_str)
                # Extract the bib key
                bib_database = bibtexparser.loads(bibtex_str)
                keys = [entry["ID"] for entry in bib_database.entries]
                bib_id = keys[0]

                # Load into the required data frame
                tex_source_name = f"{source_name}~\\cite{{{bib_id}}}"
            else:
                tex_source_name = f"{source_name}"

            # Add to the required list
            if tex_source_name not in req_metadata.keys():
                req_metadata[tex_source_name] = {
                    "url": f"{{\\footnotesize \\url{{{url_link}}}}}" if url_link.lower() != "un-specified" else f"N/A",
                    "paper_ids": [paper_id],
                    "paper_numbers": 1
                }
            else:
                req_metadata[tex_source_name]["paper_ids"].append(paper_id)
                req_metadata[tex_source_name]["paper_numbers"] += 1
 
    for source_name, meta_data in req_metadata.items():
        # Paper numbers: int -> str
        meta_data["paper_numbers"] = str(meta_data["paper_numbers"])
        # Paper citation
        meta_data["paper_ids"] = paperids2citation(meta_data["paper_ids"])
 
    # Sort by paper_numbers from largest to smallest
    # First, make sure paper_numbers is an int
    sorted_metadata = dict(
        sorted(
            req_metadata.items(),
            key=lambda item: int(item[1]["paper_numbers"]),
            reverse=True
        )
    )

    # Generate new .bib file
    new_bib_path = os.path.join(ROOT_DIR, *BIB_SAVING_DIR, new_bib_name)
    os.makedirs(os.path.dirname(new_bib_path), exist_ok=True)
    # Saved as .bib file
    with open(new_bib_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(list(set(new_bibtex))))

    print(f"Bibtex for program sources has been saved to {new_bib_path}")    

    # Generate latex table
    vertical_tables(sorted_metadata, TEMP_CONFIG["headers"], saving_path, TEMP_CONFIG["tab_space"])
 
    
def available_artifact(
    df: pd.DataFrame,
    config_data: dict, 
    saving_name: str = "rq10_available_artifacts.tex",
) -> None:

    TEMP_CONFIG = {
        "tab_space": "c p{0.99\\columnwidth}"
    }

    # Get the target data
    multi_data, saving_path = data_preprocess(
        df, 
        ["rq10_artifacts", "primary_study_id", "SE_problem"],         
        config_data, 
        ROOT_DIR, 
        TAB_SAVING_DIR,
        saving_name
    ) # type: ignore
    saving_path: str

    # Extract and parse the raw data
    artifacts = parse_column(multi_data[0])
    paper_idxes = multi_data[1]
    se_problems = parse_column(multi_data[2])
  
    tex_code = {}
    num_artifacts = 0       # Collect the number of available artifacts
    platform_counts = {}    # Counts the used platforms for artifact release
    for artifact, paper_id, se_problem in zip(artifacts, paper_idxes, se_problems):
        se_problem = f"{se_problem[0]}" 
        if len(artifact) == 0:  # Skip the invalid data
            continue
        
        num_artifacts += 1
        # Add the top content
        if se_problem not in tex_code.keys():
            tex_code[se_problem] = []
 
        url_string_list = []
        for platform, url_link_list in artifact.items():
            url_link = url_link_list[0]
            url_string_list.append(
                f"\\textit{{{platform}}}: {{\\footnotesize \\url{{{url_link}}}}}"
            )

            # Count the platforms
            if f"\\textit{{{platform}}}" not in platform_counts.keys():
                platform_counts[f"\\textit{{{platform}}}"] = 1
            else:
                platform_counts[f"\\textit{{{platform}}}"] += 1
    
        url_string = ", ".join(url_string_list)
            
        tex_code[se_problem].append(
            {
                "paper_citation": f"\\cite{{\\Paper{number2camelform(int(paper_id))}}}",
                "url": url_string
            }
        )

    # Give the additional line
    rate = num_artifacts / len(artifacts)

    sorted_items = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
    platform_str = ", ".join(f"{k} ({int(v)})" for k, v in sorted_items)
    add_platform = f"\\textbf{{Platforms: }} {platform_str}"

    additional_line = (
        f"\\multicolumn{{2}}{{l}}{{{add_platform}}} \\\\\n  "
        "\\multicolumn{2}{l}{\\textbf{Proportion of available artifacts}: "
        f"{rate*100:.1f}\\% "
        f"({num_artifacts}/{len(artifacts)})}} \\\\"
    )
        
    # Sort by paper_numbers from largest to smallest
    # First, make sure paper_numbers is an int
    sorted_metadata = dict(
        sorted(
            tex_code.items(),
            key=lambda item: len(item[1]),  # 按 value 的长度排序
            reverse=True  # 如果希望从大到小
        )
    )
    
    # Generate latex table
    vertical_grouped_table(
        sorted_metadata, 
        saving_path, 
        TEMP_CONFIG["tab_space"],
        addition_line=additional_line,
        # if_cmidrule=True
    )
 
 
if __name__ == "__main__":
    PROCEDURE = [
        ("tab", available_sources),
        ("tab", available_artifact)
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)

    print("\nRQ10 is done. \n")