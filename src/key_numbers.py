import os
from src import read_csv, read_config_json, tex_command_template, tex_file_generation

# ==============================================================
# Global variables
# ===============================================================
CONFIG_NAME = "data_attributes.json"

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
data_dir = os.path.join(root_dir, "doc", "annotated_data")

###################################################################

def boolean_data_counts(header, df):
    column_data = df[header].tolist()
    counts_yes = column_data.count("[Y]")
    counts_no = column_data.count("[N]")
    return counts_yes, counts_no

def paper_counts(configs: dict) -> list[str]:
    counts_dict = {
        "keyword": {"total": 0, "init_Y": 0, "sec_Y": 0},
        "snowballing": {"total": 0, "init_Y": 0, "sec_Y": 0}
    }
    
    file_dict = {
        "keyword": configs["keyword_name"],
        "snowballing": configs["snowballing_name"]
    }

    for search_phase, file_name in file_dict.items():
        df = read_csv(data_dir, file_name)
        csv_headers = df.columns.tolist() # type: ignore

        # Collect paper counts for initial filtering
        init_filter_header = configs["headers"]["initial_filtering"]
        sec_filter_header = configs["headers"]["second_filtering"]

        if init_filter_header in csv_headers and sec_filter_header in csv_headers:
            init_yes, init_no = boolean_data_counts(init_filter_header, df)
            sec_yes, _ = boolean_data_counts(sec_filter_header, df)

            counts_dict[search_phase]["total"] = init_yes + init_no
            counts_dict[search_phase]["init_Y"] = init_yes
            counts_dict[search_phase]["sec_Y"] = sec_yes
        else:
            print("Invalid headers")
            exit(-1)

    tex_commands = [
        tex_command_template("PaperNumKeywordInitial", str(counts_dict["keyword"]["init_Y"])),
        tex_command_template("PaperNumKeywordSecond", str(counts_dict["keyword"]["sec_Y"])),
        tex_command_template("PaperNumKeywordTotal", str(counts_dict["keyword"]["total"])),
        tex_command_template("PaperNumSnowballingInitial", str(counts_dict["snowballing"]["init_Y"])),
        tex_command_template("PaperNumSnowballingSecond", str(counts_dict["snowballing"]["sec_Y"])),
        tex_command_template("PaperNumSnowballingTotal", str(counts_dict["snowballing"]["total"])), 
        tex_command_template(
            "SizeOfLiteraturePool", str(counts_dict["keyword"]["total"] + counts_dict["snowballing"]["total"])
        ),
        tex_command_template(
            "NumberOfPrimaryStudies", str(counts_dict["keyword"]["sec_Y"] + counts_dict["snowballing"]["sec_Y"])
        )         
    ]
    return tex_commands

if __name__ == "__main__":
    # =================================================
    # Configuration
    # =================================================

    PROCEDURE = [paper_counts]
    TEX_SAVING_DIR = ["build", "latex"]
    TEX_SAVING_NAME = "numbers.tex"

    # =================================================
 
    configs = read_config_json(CONFIG_NAME)
 
    final_tex = []
    for sub_proc in PROCEDURE:
        temp_tex = sub_proc(configs)
        final_tex.extend(temp_tex)
    
    saving_dir = os.path.join(root_dir, *TEX_SAVING_DIR)
    tex_file_generation(saving_dir, TEX_SAVING_NAME, final_tex)
