import pandas as pd
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from collections import defaultdict

import os 
import unicodedata

from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
input_dir = os.path.join(root_dir, "doc", "literature_pool", "raw")
output_dir = os.path.join(root_dir, "doc", "literature_pool", "merged")

def xls2bib(file_name: str, sheet_name: Optional[str] = None):
    """
    将 Excel 文件转换为 BibTeX 文件，根据 Document Type 映射 BibTeX 类型
    """
    def row_to_bibtex(row):
        raw_type = str(row.get('Document Type', '')).strip()
        entrytype = doc_type_mapping.get(raw_type, 'misc')  # 默认 misc

        entry = {}
        entry['ENTRYTYPE'] = entrytype
        entry['ID'] = str(row.get('UT (Unique ID)', f"ID{row.name}"))
        entry['author'] = row['Authors'].replace('; ', ' and ') if isinstance(row.get('Authors'), str) else ''
        entry['title'] = row['Article Title'] if isinstance(row.get('Article Title'), str) else ''
        entry['year'] = str(int(row['Publication Year'])) if pd.notnull(row.get('Publication Year')) else ''
        entry['abstract'] = row['Abstract'] if isinstance(row.get('Abstract'), str) else ''

        # 根据类型设置出版源字段（更完整的判断）
        source = row.get('Source Title')
        if isinstance(source, str) and source.strip():
            src = source.strip()
            # 准备用于判断的 entrytype（小写）
            et = entrytype.lower()

            # 哪些 entry types 应该使用 booktitle
            booktitle_types = {'inproceedings', 'conference', 'incollection', 'inbook'}

            if et in booktitle_types:
                # 会议论文 / 书中章节：把 Source Title 当作 booktitle（所属会议或书名）
                entry['booktitle'] = src
            elif et == 'article':
                # 期刊文章：journal
                entry['journal'] = src
            elif et == 'proceedings':
                # 整个论文集（proceedings）：将 Source Title 放到 title（proceedings 的 title 字段）
                # 保留原始 title（Article Title）优先，不覆盖，如果没有则使用 Source Title
                if not entry.get('title'):
                    entry['title'] = src
                else:
                    # 如果已经有 title，可以把 proceedings 名放到 note（或 leave out）
                    entry.setdefault('note', src)
            elif et == 'book':
                # 整本书：通常 Source Title 是书名 -> 当作 title（仅当没有 Article Title 时）
                if not entry.get('title'):
                    entry['title'] = src
                else:
                    # 如果 title 已有，可能 Source Title 是出版社或丢失信息，可以放到 publisher 或 note
                    entry.setdefault('publisher', src)
            else:
                # 其它类型（techreport, phdthesis, misc 等），默认把 Source Title 放到 note（可根据需要调整）
                entry.setdefault('note', src)

        # 其他可选字段
        if pd.notnull(row.get('Volume')):
            entry['volume'] = str(int(row['Volume']))
        if pd.notnull(row.get('Issue')):
            entry['number'] = str(int(row['Issue']))
        if pd.notnull(row.get('Start Page')) and pd.notnull(row.get('End Page')):
            entry['pages'] = f"{int(row['Start Page'])}-{int(row['End Page'])}"
        if isinstance(row.get('DOI'), str):
            entry['doi'] = row['DOI']

        return entry


    # 读取 Excel 文件
    input_path =  os.path.join(input_dir, f"{file_name}.xls")
    excel_file = pd.ExcelFile(input_path)
    if sheet_name is None:
        sheet_name = excel_file.sheet_names[0] # type: ignore
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Document Type 映射到 BibTeX 类型
    doc_type_mapping = {
        'Article': 'article',
        'Review': 'article',
        'Proceedings Paper': 'inproceedings',
        'Book Chapter': 'incollection',
        'Book': 'book',
        'Editorial Material': 'misc',
        'Letter': 'misc',
        'Note': 'misc'
    }

    # 构建 BibTeX 数据库
    database = BibDatabase()
    for _, row in df.iterrows():
        database.entries.append(row_to_bibtex(row))

    output_path = os.path.join(input_dir, f"{file_name}.bib")
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as bibtex_file:
        bibtexparser.dump(database, bibtex_file)

    print(f"✅ BibTeX 文件已生成：{output_path}")


def merge_bib(bib_file_list: list[str], output_name: str):
    """
    合并多个 BibTeX 文件，根据标题去重，保留信息最完整的条目（非空字段最多）
    :param bib_file_list: List[str] 待合并的 .bib 文件路径
    :param output_file: str 输出的 BibTeX 文件路径
    """

    removed_count = 0  # 新增计数器

    def merge_entries(entry_a: dict, entry_b: dict) -> dict:
        """
        将两个 BibTeX 条目合并，字段取并集。
        若两者都有该字段，优先选非空的；若都非空，可选长度更长的版本。
        """
        nonlocal removed_count
        removed_count += 1  # 每次 merge_entries 被调用，说明 entry_b 被判定为重复

        merged = dict(entry_a)  # 先复制第一个
        for k, v in entry_b.items():
            v = str(v).strip()
            if not v:
                continue
            if k not in merged or not merged[k].strip():
                merged[k] = v
            else:
                # 如果都有值，但不同，可以选更长的那个或保留原值
                if merged[k].strip() != v and len(v) > len(merged[k]):
                    merged[k] = v
        return merged

    def normalize_title(title: str) -> str:
        """统一 title 格式，去除特殊引号、空格、大小写"""
        if not title:
            return ''
        t = title.lower().strip()
        t = unicodedata.normalize('NFKC', t)
        t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        return ''.join(ch for ch in t if ch.isalnum() or ch.isspace())  # 去掉标点

    title_dict = {}
    no_title_entries = []

    for bib_file in bib_file_list:
        bib_path = os.path.join(input_dir, bib_file)
        with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
            bib_db = bibtexparser.load(f)

        for entry in bib_db.entries:
            title_raw = entry.get('title', '').strip()
            norm_title = normalize_title(title_raw)
            if not norm_title:
                no_title_entries.append(entry)
                continue

            if norm_title in title_dict:
                title_dict[norm_title] = merge_entries(title_dict[norm_title], entry)
            else:
                title_dict[norm_title] = entry

    merged = BibDatabase()
    merged.entries = list(title_dict.values()) + no_title_entries

    merged_database = BibDatabase()
    merged_database.entries = list(title_dict.values()) + no_title_entries

    # 写入输出文件
    output_path = os.path.join(output_dir, f"{output_name}.bib")
    with open(output_path, 'w', encoding='utf-8') as f:
        bibtexparser.dump(merged_database, f)

    total_entries = len(merged_database.entries)
    print(f"✅ 合并完成，总条目数：{total_entries}")
    print(f"📄 移除/合并重复条目数：{removed_count}")
 
def bib2csv(output_name: str):
    """
    将 BibTeX 文件导入到 Excel，只保留指定列，并增加一列保存原始 BibTeX
    """
    output_path = os.path.join(output_dir, f"{output_name}.bib")
    with open(output_path, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    rows = []
    for entry in bib_database.entries:
        # 手动重建 BibTeX 字符串
        bibtex_str = f"@{entry.get('ENTRYTYPE', 'misc')}{{{entry.get('ID', '')},\n"
        for key, value in entry.items():
            if key not in ['ENTRYTYPE', 'ID']:
                bibtex_str += f"  {key} = {{{value}}},\n"
        bibtex_str += "}"

        rows.append({
            'Title': entry.get('title', ''),
            'Author': entry.get('author', ''),
            'Year': entry.get('year', ''),
            'DOI': entry.get('doi', ''),
            'Venue': entry.get('journal', entry.get('booktitle', '')),
            'Link': entry.get('url', ''),
            'Publisher': entry.get('publisher', ''),
            'Abstract': entry.get('abstract', ''),
            'BibTeX': bibtex_str  # 新增这一列
        })

    df = pd.DataFrame(rows)
    csv_file_path = os.path.join(output_dir, f"{output_name}.csv")
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

    print(f"✅ CSV 文件已生成：{csv_file_path}")

def preprocess_all(bib_file_name: str, output_name: str):
    xls2bib(bib_file_name)
    bib_files = ["acm.bib", "ieee.bib", "wiley.bib", f"{bib_file_name}.bib"]
    merge_bib(bib_files, output_name)
    bib2csv(output_name)

if __name__ == "__main__":
    input_name = "wos"
    output_name = "remove_duplication"
    preprocess_all(input_name, output_name)
