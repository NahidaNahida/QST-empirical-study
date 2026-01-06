"""
Docstring for src.data_frame
Data frame related utilities for data preprocessing and parsing.
"""

import re
import pandas as pd
import os 
from typing import Any, Dict, List, Tuple, Literal
 

def data_clean(data: list[str], mode: Literal["all", "outer"]="all") -> list[str]:
    if mode == "all":   # Remove all existing "[" and "]"
        clean_data = [item.replace("[", "").replace("]", "") for item in data]
    elif mode == "outer":   # Only remove "[" and "]" at the outermost positions
        clean_data = []
        for item in data:
            item = item.strip()
            if item.startswith("[") and item.endswith("]"):
                clean_data.append(item[1:-1].strip())
            else:
                clean_data.append(item)
    return clean_data
 
def data_preprocess(
    df: pd.DataFrame,
    header_item: str | list[str],
    config_data: dict,
    root_dir: str,
    saving_dir: list[str],
    saving_name: str | list[str]
) -> tuple[Any, Any]:
    """Preprocess data for plotting and return required data and saving path."""
    # Data section
    if isinstance(header_item, str):
        header = config_data["headers"][header_item]
        req_data = df[header].tolist()
    else:
        req_data = [
            df[config_data["headers"][temp_item]].tolist()
            for temp_item in header_item
        ]

    # Path section
    if isinstance(saving_name, str):
        saving_path = os.path.join(root_dir, *saving_dir, saving_name)
    else:
        saving_path = [
            os.path.join(root_dir, *saving_dir, temp_name)
            for temp_name in saving_name
        ]

    return req_data, saving_path

import re

def parse_data_str(
    metadata: str,
    skip_invalid_key: bool = True,
    skip_invalid_value: bool = True
) -> dict | list:
    """
    Parse multiple square bracket [] blocks in a string.
    Each block follows the format: [key: val1, val2, ...]
    - Support nested [] but only capture the outermost blocks
    - Skip content inside <...> (may contain commas)
    - If skip_invalid_key=True, ignore keys that are 'Un-specified' (case-insensitive)
    - If skip_invalid_value=True, ignore values that are 'Un-specified'
    - If skip_invalid_key=True and the block is [Un-specified], skip the entire block
    - Ensure the content inside [] remains intact (even if it contains commas),
      and preserve its original format
    - If the input is in the form [Quantum state], [Quantum gate] (no colon),
      return a list
    """

    result = {}

    # --- Extract outermost [] blocks ---
    blocks, stack, current = [], 0, []
    for ch in metadata:
        if ch == "[":
            if stack == 0:
                current = []
            stack += 1

        if stack > 0:
            current.append(ch)

        if ch == "]":
            stack -= 1
            if stack == 0:
                block_str = "".join(current)
                inner_text = block_str[1:-1].strip()
                if skip_invalid_key and inner_text.lower() == "un-specified":
                    continue
                blocks.append(inner_text)
                current = []

    # --- Intelligent comma split ignoring nested [] ---
    def smart_split(s: str):
        parts, buf, depth = [], [], 0
        for ch in s:
            if ch == "[":
                depth += 1
                buf.append(ch)
            elif ch == "]":
                depth -= 1
                buf.append(ch)
            elif ch == "," and depth == 0:
                part = "".join(buf).strip()
                if part:
                    parts.append(part)
                buf = []
            else:
                buf.append(ch)
        if buf:
            parts.append("".join(buf).strip())
        return parts

    # --- Parse key/value blocks ---
    for block in blocks:
        if ":" not in block:
            continue

        key, values = block.split(":", 1)
        key = key.strip()
        # Remove <...> from key
        key = re.sub(r"<.*?>", "", key).strip()

        if skip_invalid_key and key.lower() == "un-specified":
            continue

        # Remove <...> from values
        cleaned_values = re.sub(r"<.*?>", "", values)

        items = [v for v in smart_split(cleaned_values) if v]

        if skip_invalid_value:
            items = [v for v in items if v.strip().lower() != "un-specified"]

        if skip_invalid_value and not items:
            continue

        result.setdefault(key, []).extend(items)

    # --- If there is no key:value format, return a list ---
    if not result and blocks:
        if all(":" not in b for b in blocks):
            all_values = []
            for b in blocks:
                inner = re.sub(r"<.*?>", "", b).strip()
                if inner and (not skip_invalid_value or inner.lower() != "un-specified"):
                    all_values.extend(smart_split(inner))
            return all_values

    return result


def parse_column(target_data: list[str], skip_invalid_key: bool=True, skip_invalid_value: bool=True):
    """Invalid data will return '{}'."""
    parsed_metadata = []
    for metadata in target_data:
        # Judge whether the data is valid for parsing, i.e., in the form of "[]".
        # This can directly exclude values such as "N/A".
        if ('['  in str(metadata) 
            and ']' in str(metadata) 
            and metadata.lower() not in ["[none]", "[un-specified]"]): 
            parsed_metadata.append(parse_data_str(
                metadata, 
                skip_invalid_key=skip_invalid_key,
                skip_invalid_value=skip_invalid_value
            ))
        else:
            parsed_metadata.append({})
    return parsed_metadata

 

def get_min_max(num_list):
    """
    Given a list whose elements may be:
    - '123'
    - 'From 100 to 200'
    Return the (min, max) of all numerical values found.
    """
    numbers = []

    for item in num_list:
        if not item or not isinstance(item, str):
            continue

        item = item.strip()

        # Match "From X to Y"
        match = re.search(r"[Ff]rom\s*([-\d\.]+)\s*[Tt]o\s*([-\d\.]+)", item)
        if match:
            x, y = match.groups()
            try:
                x, y = float(x), float(y)
                numbers.extend([x, y])
            except ValueError:
                continue
        else:
            # Try to directly parse as a number
            try:
                numbers.append(float(item))
            except ValueError:
                continue

    if not numbers:
        return None, None

    return min(numbers), max(numbers)

def dict2upsetform(
    data_dict: Dict[str, List[Any]]
) -> Tuple[List[List[str]], List[int]]:
    """
    Convert multiple lists (each containing n sets) into:
    - A list of column name combinations, e.g., [['A'], ['A', 'B']]
    - A list of occurrence counts corresponding to each combination

    Parameters:
      data_dict: dict[str, list], each key corresponds to a list
    """

    # Default markers for "invalid data"
    invalid_mark = (None, {}, set())  # Can be extended, e.g., to include np.nan

    # Check whether all lists have the same length
    lengths = [len(v) for v in data_dict.values()]
    if len(set(lengths)) != 1:
        raise ValueError("All lists must be of the same length")
    
    # Construct a boolean matrix: True indicates valid data
    df = pd.DataFrame({
        k: [not (x in invalid_mark or (isinstance(x, set) and len(x) == 0))
            for x in v]
        for k, v in data_dict.items()
    })
    
    # Combination for each row (which columns are True)
    combos = []
    for _, row in df.iterrows():
        combo = tuple(col for col, val in row.items() if val)
        combos.append(combo)
    
    # Count frequencies
    freq = pd.Series(combos).value_counts()
    
    # Output two lists
    combo_list = [list(k) for k in freq.index]
    count_list = freq.values.tolist()
    
    return combo_list, count_list

if __name__ == "__main__":
    # Unit testing process

    def unittest0():
        unittest = [
            "[300, 233, From 6 to 66]", 
            "[Un-specified]", 
            "[Un-specified: 456]", 
            "[Quantum state]",
            "[Quantum state], [Quantum gate]",
            "[Quantum state], [Quantum gate: 200]",
            "[Wrong output oracle: None], [Output probability oracle: Un-specified]",
            "[20, 30]",
            "[Ouput probability oracle: Un-specified]",
            "[Quantum algorithms and subroutines: Hadamard Test, Superdense Coding, Un-specified]",
            "[Specific: [H gates: 233], [Pauli-X gates]]"
        ]
        print(parse_column(unittest))
        print(parse_column(unittest, skip_invalid_key=False))
        print(parse_column(unittest, skip_invalid_value=False))

    def unittest1():
        unittest = [
            ["300", "233", "From 100 to 400", "500"],
            ["From 1 to 32", "1", "3", "From 30 to 312"],
            ["2"] 
        ]
        for metatest in unittest:
            print(get_min_max(metatest))
    
    PROC = [unittest0]
    for sub_proc in PROC:
        sub_proc()
