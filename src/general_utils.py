import os
import pandas as pd
import json
from typing import Optional
from pathlib import Path

def read_csv(
    file_dir: str, file_name: str, encoding='utf-8'
) -> Optional[pd.DataFrame]:
    # Build the full directory path
    file_path = os.path.join(file_dir, file_name)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def read_config_json(file_name: str) -> dict:
    # Get the current directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the parent directory (project root)
    path_dir = os.path.dirname(current_dir)
    
    # Build the full path to the config file
    config_path = os.path.join(path_dir, "config", file_name)
    
    # Check if the file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Read and parse the JSON config file
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        exit(-1)
    except Exception as e:
        print(f"Error reading config file: {e}")
        exit(-1)
        
def tex_command_template(command_name: str, value: str) -> str:
    return f"\\newcommand{{\\{command_name}}}{{{value}\\xspace}}"

def tex_file_generation(
    file_dir: str, 
    file_name: str, 
    lines: list[str], 
    encoding='utf-8', 
    ensure_trailing_newline=True
) -> None:
    """
    Write a list of strings (each representing one line of LaTeX code)
    to a .tex file at `filepath`.
    """
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, file_name)
    text_lines = [str(l).rstrip("\r\n") for l in lines]
    text = "\n".join(text_lines)
    if ensure_trailing_newline and not text.endswith("\n"):
        text += "\n"
    with open(file_path, "w", encoding=encoding, newline="\n") as f:
        f.write(text)
