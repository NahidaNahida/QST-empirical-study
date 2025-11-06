import re
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bparser import BibTexParser
from titlecase import titlecase


# === 常量定义 ===
SPECIAL_TERMS = {"IEEE", "ACM", "ICSE", "ASE", "FSE", "DAC", "ISSTA", "CVPR", "NIPS", "NeurIPS"}
PROPER_NOUNS = {"BERT", "GPT", "Google", "OpenAI", "Transformer", "ChatGPT"}


# === 文本规范化工具 ===
def smart_title_case(text: str) -> str:
    """
    对会议 / 期刊名进行智能标题大小写转换：
    - 使用 titlecase；
    - 保留缩写词和专有名词；
    - 忽略大括号或括号中的内容；
    - 若结尾有括号（常用于缩写，如 "(ICSE)"），则保持括号部分不变。
    """
    if not text:
        return text

    placeholders = {}

    # 检查末尾是否有括号部分，如 "(ICSE)"
    match_suffix = re.search(r'(\s*\([^()]+\)\s*)$', text)
    suffix = ""
    if match_suffix:
        suffix = match_suffix.group(1)
        text = text[:match_suffix.start()]  # 仅保留括号前部分

    # 保护花括号或圆括号中的内容（防止被错误改大小写）
    def protect(match):
        key = f"__PLACEHOLDER_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    text_protected = re.sub(r'({[^{}]+}|\([^()]+\))', protect, text)
    text_cased = titlecase(text_protected)

    # 恢复缩写和专有名词
    for term in SPECIAL_TERMS | PROPER_NOUNS:
        pattern = re.compile(r'\b' + re.escape(term.lower()) + r'\b', re.IGNORECASE)
        text_cased = pattern.sub(term, text_cased)

    # 恢复保护内容
    for key, val in placeholders.items():
        text_cased = text_cased.replace(key, val)

    # 拼回末尾的括号部分
    return text_cased.strip() + ("" if not suffix else " " + suffix.strip())


def smart_sentence_case(text: str) -> str:
    """
    将标题改为句式大小写（首字母大写 + 保留缩写词/专有名词）。
    """
    if not text:
        return text

    stripped = text.strip("{} ")
    if not stripped:
        return text

    cased = stripped[0].upper() + stripped[1:]

    for term in SPECIAL_TERMS | PROPER_NOUNS:
        pattern = re.compile(r'\b' + re.escape(term.lower()) + r'\b', re.IGNORECASE)
        cased = pattern.sub(term, cased)

    return cased


# === 主函数 ===
def normalize_bibtex_str(bib_str: str) -> str:
    """
    输入 BibTeX 字符串（可包含多条条目），返回处理后的 BibTeX 字符串。
    - 标题改为句式大小写；
    - 期刊 / 会议名改为标题大小写；
    """
    parser = BibTexParser(common_strings=True)
    bib_db = bibtexparser.loads(bib_str, parser=parser)

    for entry in bib_db.entries:
        # 标题
        if "title" in entry:
            entry["title"] = smart_sentence_case(entry["title"])
        # 会议 / 期刊名
        for field in ["journal", "booktitle"]:
            if field in entry:
                entry[field] = smart_title_case(entry[field])

    # 输出新 BibTeX
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None # type: ignore
    writer.add_trailing_comma = False

    return writer.write(bib_db).strip()


if __name__ == "__main__":
    # Unit test
    raw_bib = """
    @inproceedings{example2025,
      title={a study on transformer and gpt models},
      author={Li, Hua and Zhang, Wei},
      booktitle={ieee international conference on software engineering (icse)},
      year={2025}
    }

    @article{smith2024,
      title={the future of ai research at openai},
      journal={acm transactions on artificial intelligence},
      year={2024}
    }
    """
    result = normalize_bibtex_str(raw_bib)
    print(result)
