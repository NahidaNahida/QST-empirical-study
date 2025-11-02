import os
from src import read_csv, read_config_json, tex_command_template, tex_file_generation
from num2words import num2words
import bibtexparser
import re

# ==============================================================
# Global variables
# ===============================================================
CONFIG_NAME = "data_attributes.json"

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
data_dir = os.path.join(root_dir, "doc", "annotated_data")

###################################################################

def normalize_bib_key(entry: dict[str, str]) -> str:
    """
    Normalize the BibTeX key according to Google Scholar style.
    Format: LastnameYYYYFirstWordOfTitle
    """
    author = entry.get("author", "").split(" and ")[0]  # Take the first author
    first_author = author.split(" and ")[0].strip()

    # Determine if it is in the "Last, First" format
    if ',' in first_author:
        last_name = first_author.split(',')[0].strip()
    else:
        last_name = first_author.split()[-1].strip() if first_author else "unknown"

    # Clear non-alphabetic characters
    last_name = re.sub(r"[^a-zA-Z]", "", last_name)

    year = entry.get("year", "noyear")

    # Extract the first English word of the title
    title = entry.get("title", "")
    title_first = re.sub(r"[^a-zA-Z]", "", title.split()[0]) if title else "Untitled"

    # Splicing the new key
    new_key = f"{last_name}{year}{title_first}".lower()
    return new_key


def bib_file(configs: dict, saving_dir: str, saving_name: str="primary_studies.bib") -> None:
    file_name = configs["final_list_name"]
    header = configs["headers"]["bibtex"]

    # Readin the data
    df = read_csv(data_dir, file_name)
    bibtex_list = df[header].tolist()

    # Output to the saving path
    os.makedirs(saving_dir, exist_ok=True) # Check the existence of the target directory
    saving_path = os.path.join(saving_dir, saving_name)
    with open(saving_path, "w", encoding="utf-8") as f:
        for bib_entry in bibtex_list:
            bib_db = bibtexparser.loads(bib_entry)
            entry = bib_db.entries[0]

            # 获取标准化的 key
            new_key = normalize_bib_key(entry)

            # 替换旧 key
            entry["ID"] = new_key

            # 将修改后的 entry 转回字符串
            bib_str = bibtexparser.dumps(bib_db)

            # 写入文件
            f.write(bib_str.strip() + "\n\n")

    print(f"There are {len(bibtex_list)} pieces of literature saved at {saving_path}.")

def id_commands(configs: dict, saving_dir: str, saving_name: str="paper_ids.tex") -> None:
    file_name = configs["final_list_name"]
    bib_header = configs["headers"]["bibtex"]
    id_header = configs["headers"]["primary_study_id"]

    # Readin the data
    df = read_csv(data_dir, file_name)
    bib_list = df[bib_header].tolist()
    id_list = df[id_header]

    # Generate tex commands
    tex_commands = []
    for idx, bib in zip(id_list, bib_list):
        # Transfer the number to corresponding English word
        word = num2words(int(idx), lang="en")

        # Remove the hyphens and capitalize the first letter of each word
        camel_case_word = ''.join(word.capitalize() for word in word.replace('-', ' ').split())

        # Parse bib entries
        bib_db = bibtexparser.loads(bib)
        entry = bib_db.entries[0]

        # Generate normalized keys with the same style to Google Scholar
        normalized_key = normalize_bib_key(entry)

        # Generate Latex commends
        tex_commands.append(
            tex_command_template(f"Paper{camel_case_word}", normalized_key)
        )

    tex_file_generation(saving_dir, saving_name, tex_commands)
    print(f"Commands for paper IDs are created.")

if __name__ == "__main__":
    # =================================================
    # Configuration
    # =================================================

    PROCEDURE = ["bib", "id"]
    
    PROC_CONFIG = {
        "bib": {"func": bib_file, "dir": ["build", "bib"]},
        "id":  {"func": id_commands, "dir": ["build", "latex"]}
    }
 
    # =================================================
 
    configs = read_config_json(CONFIG_NAME)
    for sub_proc_name in PROCEDURE:
        sub_proc = PROC_CONFIG[sub_proc_name]["func"]
        dir_list = PROC_CONFIG[sub_proc_name]["dir"]
        saving_dir = os.path.join(root_dir, *dir_list)
        sub_proc(configs, saving_dir)