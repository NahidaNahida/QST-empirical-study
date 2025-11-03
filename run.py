import bibtexparser
from bibtexparser.bwriter import BibTexWriter  # ✅ 用 writer 而非 dump
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogenize_latex_encoding
import sys
import os
import re

from titlecase import titlecase


# 常见小词（不应大写，除非是首词或尾词）
STOPWORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "in",
    "nor", "of", "on", "or", "so", "the", "to", "up", "yet", "with"
}

SPECIAL_TERMS = {"IEEE", "ACM", "ICSE", "ASE", "FSE", "DAC", "ISSTA", "CVPR", "NIPS", "NeurIPS"}

# 专有名词列表：title 中首字母保持大写
PROPER_NOUNS = {"BERT", "GPT", "Google", "OpenAI", "Transformer", "ChatGPT"}



def smart_title_case(text: str) -> str:
    """
    使用 titlecase 库将文本转换为标题大小写，
    并保留特殊缩写词（SPECIAL_TERMS）和专有名词（PROPER_NOUNS）
    """
    # 首先保护 LaTeX 或大括号内容
    placeholders = {}

    def protect(match):
        key = f"__PLACEHOLDER_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    text_protected = re.sub(r'({[^{}]+}|\([^()]+\))', protect, text)

    # titlecase 自动处理常见小写词
    text_cased = titlecase(text_protected)

    # 替换专有名词 / 缩写词
    for term in SPECIAL_TERMS | PROPER_NOUNS:
        pattern = re.compile(r'\b' + re.escape(term.lower()) + r'\b', re.IGNORECASE)
        text_cased = pattern.sub(term, text_cased)

    # 恢复保护内容
    for key, val in placeholders.items():
        text_cased = text_cased.replace(key, val)

    return text_cased
 


def is_arxiv_entry(entry: dict) -> bool:
    """
    判断是否为arXiv条目：
    - 包含 archivePrefix / eprinttype / howpublished 字段
    - eprint 字段中含 arxiv
    - journal 字段含 arXiv 且带有编号
    """
    archive_prefix = entry.get('archivePrefix', '').lower()
    eprint_type = entry.get('eprinttype', '').lower()
    entry_type = entry.get('ENTRYTYPE', '').lower()

    if 'arxiv' in archive_prefix or 'arxiv' in eprint_type:
        return True
    if entry_type == 'misc' and 'arxiv' in entry.get('howpublished', '').lower():
        return True
    if 'arxiv' in entry.get('eprint', '').lower():
        return True

    # ✅ 增加 journal 中包含 arXiv 标识的判断
    if 'journal' in entry and re.search(r'arxiv.*?(?:\d{4}\.\d{4,5}|[a-z\-]+/\d{7})', entry['journal'], re.IGNORECASE):
        return True

    return False



def normalize_arxiv_entry(entry: dict):
    """
    标准化 arXiv 条目，使其符合 GB/T 7714-2015 格式：
    - journal 设为 arXiv
    - howpublished 设为 [J/OL]
    - note 设为 arXiv:编号
    - ENTRYTYPE 设为 misc
    """
    arxiv_id = None

    # 优先使用 eprint 字段
    if 'eprint' in entry:
        arxiv_id = entry['eprint']

    # 尝试从 journal 字段中提取 arXiv ID（支持旧格式和新格式）
    elif 'journal' in entry and 'arxiv' in entry['journal'].lower():
        match = re.search(
            r'(?:arxiv\s*preprint\s*)?(?P<id>\d{4}\.\d{4,5}|[a-z\-]+(?:\.[a-z]+)?/\d{7})',
            entry['journal'], re.IGNORECASE
        )
        if match:
            arxiv_id = match.group('id')

    # 如能获取 arXiv ID，填充新字段
    if arxiv_id:
        entry['journal'] = "arXiv"
        entry['howpublished'] = "[J/OL]"
        entry['note'] = f"arXiv:{arxiv_id}"
        entry['ENTRYTYPE'] = 'misc'  # 类型统一设为 misc

    # 若 year 缺失则尝试从 date 中提取
    if 'year' not in entry and 'date' in entry:
        match = re.search(r"\d{4}", entry['date'])
        if match:
            entry['year'] = match.group(0)

    # 移除不再需要的字段（可选）
    for field in ['eprinttype', 'archivePrefix']:
        if field in entry:
            del entry[field]


def process_bib_file(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as bibtex_file:
        parser = BibTexParser()
        # ❌ 不使用 parser.customization = homogenize_latex_encoding
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    for entry in bib_database.entries:
        # arXiv 特殊处理：优先处理，避免 journal 被错误格式化
        is_arxiv = is_arxiv_entry(entry)
        if is_arxiv:
            normalize_arxiv_entry(entry)

        # 会议与期刊名格式化（跳过 arXiv 条目）
        for field in ['booktitle', 'journal']:
            if field in entry and not is_arxiv:
                entry[field] = smart_title_case(entry[field])

        # 标题处理
        if 'title' in entry:
            entry['title'] = smart_sentence_case(entry['title'])


    # ✅ 使用 BibTexWriter 替代 dump，避免乱码
    writer = BibTexWriter()
    writer.indent = '  '                 # 缩进
    writer.order_entries_by = None      # 保持原顺序
    writer.add_trailing_comma = False   # 去除最后逗号（更符合国标）

    with open(output_file, 'w', encoding='utf-8') as bibtex_file:
        bibtex_file.write(writer.write(bib_database))

    print(f"✅ 已处理完成，结果保存在 {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python capitalize_venue.py <输入.bib文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not input_file.endswith('.bib'):
        print("请输入 .bib 格式的文件")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + '_capitalized.bib'
    process_bib_file(input_file, output_file)
