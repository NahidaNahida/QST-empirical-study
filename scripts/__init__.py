# scripts\__init__.py
import os

FILE_DICT = {
    "FILE_DIR": ["doc", "annotated_data"],
    "FILE_NAME": "final_list.csv"
}

CONFIG_DICT = {
    "CONFIG_DIR": ["config"],
    "CONFIG_DATA_NAME": "data_attributes.json",
    "CONFIG_FIGURE_NAME": "figure_style.json"
}

SAVING_DIR = ["build", "figures"]

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_DIR = os.path.join(ROOT_DIR, *FILE_DICT["FILE_DIR"])
FILE_NAME = FILE_DICT["FILE_NAME"]
CONFIG_DATA_NAME = CONFIG_DICT["CONFIG_DATA_NAME"]
CONFIG_FIGURE_NAME = CONFIG_DICT["CONFIG_FIGURE_NAME"]

__all__ = [
    "ROOT_DIR",
    "FILE_DIR",
    "FILE_NAME",
    "CONFIG_DATA_NAME",
    "CONFIG_FIGURE_NAME",
    "SAVING_DIR"
]
