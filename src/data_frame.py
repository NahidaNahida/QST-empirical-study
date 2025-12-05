import re
import pandas as pd
import os 
from typing import Any, Dict, List, Tuple, Union, Iterable, Optional, overload, Literal
 

def data_clean(data: list[str], mode: Literal["all", "outer"]="all") -> list[str]:
    if mode == "all":   # Remove all the existing "[" and "]"
        clean_data = [item.replace("[", "").replace("]", "") for item in data]
    elif mode == "outer":   # Merely remove "[" and "]" at the outermost position
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
    # --- 数据部分 ---
    if isinstance(header_item, str):
        header = config_data["headers"][header_item]
        req_data = df[header].tolist()
    else:
        req_data = [
            df[config_data["headers"][temp_item]].tolist()
            for temp_item in header_item
        ]

    # --- 路径部分 ---
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
    Parse multiple square brackets [] blocks in a string.
    Each block is in the format of [key: val1, val2, ...]
    - Support nested [] but only capture outermost blocks
    - Skip content inside <...> (may contain commas)
    - If skip_invalid_key=True, ignore keys that are 'Un-specified' (case-insensitive)
    - If skip_invalid_value=True, ignore values that are 'Un-specified'
    - If skip_invalid_key=True and the block is [Un-specified], skip entirely
    - 保证 [] 内部的内容完整（即使包含逗号），并保留其原始格式
    - 若输入形如 [Quantum state], [Quantum gate]（无冒号），则返回 list
    """

    result = {}

    # --- 提取最外层 [] ---
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
        # remove <...> from key
        key = re.sub(r"<.*?>", "", key).strip()

        if skip_invalid_key and key.lower() == "un-specified":
            continue

        # remove <...> from values
        cleaned_values = re.sub(r"<.*?>", "", values)

        items = [v for v in smart_split(cleaned_values) if v]

        if skip_invalid_value:
            items = [v for v in items if v.strip().lower() != "un-specified"]

        if skip_invalid_value and not items:
            continue

        result.setdefault(key, []).extend(items)

    # --- 若没有 key:value 格式，则返回 list ---
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
    """Invalid data will return "{}."""
    parsed_metadata = []
    for metadata in target_data:
        # Jugde the valid data for parse, i.e., in the form of "[]".
        # This can directly exclude "N/A".
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


import re

def get_min_max(num_list):
    """
    给定一个list，元素可能为：
    - '123'
    - 'From 100 to 200'
    返回所有数值的 (min, max)
    """
    numbers = []

    for item in num_list:
        if not item or not isinstance(item, str):
            continue

        item = item.strip()

        # 匹配 "From X to Y"
        match = re.search(r"[Ff]rom\s*([-\d\.]+)\s*[Tt]o\s*([-\d\.]+)", item)
        if match:
            x, y = match.groups()
            try:
                x, y = float(x), float(y)
                numbers.extend([x, y])
            except ValueError:
                continue
        else:
            # 尝试直接解析为数字
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
    将多个列表(每个含n个集合)转换为：
      1️⃣ 各组合的列名列表，如 [['A'], ['A', 'B']]
      2️⃣ 对应每个组合的出现次数列表

    参数:
      data_dict: dict[str, list]，每个键对应一个列表
    """

    # 默认的“无效数据”标志集合
    invalid_mark = (None, {}, set())  # 可根据需要扩展，比如加上 np.nan

    # 检查各列表长度是否一致
    lengths = [len(v) for v in data_dict.values()]
    if len(set(lengths)) != 1:
        raise ValueError("All lists must be of the same length")
    
    # 构造布尔矩阵：True 表示有效数据
    df = pd.DataFrame({
        k: [not (x in invalid_mark or (isinstance(x, set) and len(x) == 0))
            for x in v]
        for k, v in data_dict.items()
    })
    
    # 每一行的组合（哪些列为 True）
    combos = []
    for _, row in df.iterrows():
        combo = tuple(col for col, val in row.items() if val)
        combos.append(combo)
    
    # 统计频数
    freq = pd.Series(combos).value_counts()
    
    # 输出两个列表
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