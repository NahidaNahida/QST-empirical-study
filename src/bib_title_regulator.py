"""
Docstring for src.bib_title_regulator
Utilities for normalizing titles in BibTeX entries.
"""

import re
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bparser import BibTexParser
from titlecase import titlecase


# === Constant Definitions ===
SPECIAL_TERMS = {"IEEE", "ACM", "ICSE", "ASE", "FSE", "DAC", "ISSTA", "CVPR", "NIPS", "NeurIPS"}
PROPER_NOUNS = {"BERT", "GPT", "Google", "OpenAI", "Transformer", "ChatGPT"}


# === Text Normalization Utilities ===
def smart_title_case(text: str) -> str:
    """
    Perform intelligent title casing for conference / journal names:
    - Use `titlecase`;
    - Preserve acronyms and proper nouns;
    - Ignore content inside braces or parentheses;
    - If the text ends with parentheses (commonly used for abbreviations, e.g., "(ICSE)"),
      keep the parenthesized part unchanged.
    """
    if not text:
        return text

    placeholders = {}

    # Check if there is a trailing parenthesized suffix, e.g., "(ICSE)"
    match_suffix = re.search(r'(\s*\([^()]+\)\s*)$', text)
    suffix = ""
    if match_suffix:
        suffix = match_suffix.group(1)
        text = text[:match_suffix.start()]  # Keep only the part before parentheses

    # Protect content inside braces or parentheses (to avoid incorrect casing)
    def protect(match):
        key = f"__PLACEHOLDER_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    text_protected = re.sub(r'({[^{}]+}|\([^()]+\))', protect, text)
    text_cased = titlecase(text_protected)

    # Restore acronyms and proper nouns
    for term in SPECIAL_TERMS | PROPER_NOUNS:
        pattern = re.compile(r'\b' + re.escape(term.lower()) + r'\b', re.IGNORECASE)
        text_cased = pattern.sub(term, text_cased)

    # Restore protected content
    for key, val in placeholders.items():
        text_cased = text_cased.replace(key, val)

    # Append the trailing parenthesized suffix back
    return text_cased.strip() + ("" if not suffix else " " + suffix.strip())


def smart_sentence_case(text: str) -> str:
    """
    Convert a title to sentence case (capitalize the first letter while
    preserving acronyms and proper nouns).
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


# === Main Function ===
def normalize_bibtex_str(bib_str: str) -> str:
    """
    Take a BibTeX string (possibly containing multiple entries) and return
    a normalized BibTeX string:
    - Titles are converted to sentence case;
    - Journal / conference names are converted to title case.
    """
    parser = BibTexParser(common_strings=True)
    bib_db = bibtexparser.loads(bib_str, parser=parser)

    for entry in bib_db.entries:
        # Title
        if "title" in entry:
            entry["title"] = smart_sentence_case(entry["title"])
        # Conference / journal name
        for field in ["journal", "booktitle"]:
            if field in entry:
                entry[field] = smart_title_case(entry[field])

    # Output the new BibTeX
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None  # type: ignore
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
