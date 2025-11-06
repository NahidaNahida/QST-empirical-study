"""
Code for the data analysis of RQ1 Quantum Programs
"""

from src import (
    read_csv, read_config_json, data_clean,
    line_chart, pie_chart, horizontal_bar_chart, horizontal_boxplot,
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
    )

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
                    "url": f"\\footnotesize{{\\url{{{url_link}}}}}" if url_link.lower() != "un-specified" else f"List",
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
 
    


if __name__ == "__main__":
    PROCEDURE = [
        # ("fig", algorithm_and_subroutine_names),
        # ("fig", number_of_objects),
        ("tab", available_sources),
    ]

    df = read_csv(FILE_DIR, FILE_NAME)
    config_data = read_config_json(CONFIG_DATA_NAME)
    config_figure = read_config_json(CONFIG_FIGURE_NAME)
    
    for type, sub_proc in PROCEDURE:
        if type == "fig":
            sub_proc(df, config_data, config_figure) # type: ignore
        elif type == "tab":
            sub_proc(df, config_data)