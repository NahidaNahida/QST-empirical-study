import re
import pandas as pd
import os 
from typing import Literal
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
    header_item: str, 
    config_data: dict,
    root_dir: str,
    saving_dir: list, 
    saving_name: str
) -> tuple[list, str]:
    header = config_data["headers"][header_item]
    req_data = df[header].tolist()
    saving_path = os.path.join(root_dir, *saving_dir, saving_name)
    return req_data, saving_path

def parse_to_dict(metadata: str, skip_invalid_key: bool = True):
    """
    Parse multiple square brackets [] blocks in a string.
    Each block is in the format of [key: val1, val2, ...]
    - Support nested [] but only capture outermost blocks
    - Skip content inside <...> (may contain commas)
    - If skip_invalid_key=True, ignore keys that are 'Un-specified' (case-insensitive)
    - If the block is [Un-specified], skip entirely
    - 保证 [] 内部的内容完整（即使包含逗号），并保留其原始格式
    """
    result = {}

    # --- 自定义解析逻辑：逐字符扫描最外层 [] ---
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
                if inner_text.lower() == "un-specified":
                    continue
                blocks.append(inner_text)
                current = []

    # --- 函数：安全地分割 value（忽略 [] 内部的逗号） ---
    def smart_split(s):
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

    # --- 处理每个块 ---
    for block in blocks:
        if ":" not in block:
            continue

        key, values = block.split(":", 1)
        key = key.strip()
        if skip_invalid_key and key.lower() == "un-specified":
            continue

        # 删除 <...> 结构（非贪婪）
        cleaned_values = re.sub(r"<.*?>", "", values)

        # 智能分割
        items = [v for v in smart_split(cleaned_values) if v]

        result.setdefault(key, []).extend(items)

    # 移除 value 为 ["Un-specified"] 的键值对, e.g., 'Quantum algorithms and subroutines': ['Un-specified']
    result = {k: v for k, v in result.items() if str(v[0]).strip().lower() != "un-specified"}
    return result

def parse_column(target_data: list[str], skip_invalid_data: bool=True) -> list[dict]:
    """Invalid data will return "{}."""
    parsed_metadata = []
    for metadata in target_data:
        # Jugde the valid data for parse, i.e., in the form of "[]".
        # This can directly exclude "N/A".
        if ('['  in str(metadata) 
            and ']' in str(metadata) 
            and metadata.lower() not in ["[none]", "[un-specified]"]): 
            parsed_metadata.append(parse_to_dict(metadata, skip_invalid_key=skip_invalid_data))
        else:
            parsed_metadata.append({})
    return parsed_metadata

if __name__ == "__main__":
    # Unit testing
    data = (
        "[Quantum algorithms and subroutines: "
        "Hadamard Test, Superdense Coding, Quantum Amplitude Amplification, "
        "One Qubit Error Correction for Bit Flip, Quantum Fourier Transform, "
        "Quantum Phase Estimation],"
        "[Quantum states: '|0>', '|1>'],"
        "[Quantum gates: 'X', Un-specified, 'H'],"
        "[Un-specified: 23],"
        "[Un-specified],"
        "[Shots: 200, 300],"
        "[Qiskit aqua library: [Un-specified], https://github.com/qiskit-community/qiskit-aqua#migration-guide]"
    )
    # data = "[Un-specified]"
    print(parse_to_dict(data))
    print(parse_to_dict(data, skip_invalid_key=False))