"""
Docstring for src.preprocesssing
Utilities for preprocessing bibliographic data from Excel to BibTeX and CSV formats.
"""

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
    Convert an Excel file to a BibTeX file, mapping Document Type to BibTeX entry types.
    """
    def row_to_bibtex(row):
        raw_type = str(row.get('Document Type', '')).strip()
        entrytype = doc_type_mapping.get(raw_type, 'misc')  # default: misc

        entry = {}
        entry['ENTRYTYPE'] = entrytype
        entry['ID'] = str(row.get('UT (Unique ID)', f"ID{row.name}"))
        entry['author'] = row['Authors'].replace('; ', ' and ') if isinstance(row.get('Authors'), str) else ''
        entry['title'] = row['Article Title'] if isinstance(row.get('Article Title'), str) else ''
        entry['year'] = str(int(row['Publication Year'])) if pd.notnull(row.get('Publication Year')) else ''
        entry['abstract'] = row['Abstract'] if isinstance(row.get('Abstract'), str) else ''

        # Set publication source fields based on entry type (more comprehensive rules)
        source = row.get('Source Title')
        if isinstance(source, str) and source.strip():
            src = source.strip()
            # Prepare entry type for comparison (lowercase)
            et = entrytype.lower()

            # Entry types that should use booktitle
            booktitle_types = {'inproceedings', 'conference', 'incollection', 'inbook'}

            if et in booktitle_types:
                # Conference papers / book chapters: use Source Title as booktitle
                entry['booktitle'] = src
            elif et == 'article':
                # Journal articles
                entry['journal'] = src
            elif et == 'proceedings':
                # Entire proceedings volume: put Source Title into title if not already present
                # Preserve the original title (Article Title) if it exists
                if not entry.get('title'):
                    entry['title'] = src
                else:
                    # If title already exists, store proceedings name in note (or leave out)
                    entry.setdefault('note', src)
            elif et == 'book':
                # Whole book: Source Title is usually the book title
                if not entry.get('title'):
                    entry['title'] = src
                else:
                    # If title already exists, Source Title may be publisher or missing info
                    entry.setdefault('publisher', src)
            else:
                # Other types (techreport, phdthesis, misc, etc.)
                # Default: put Source Title into note (can be adjusted if needed)
                entry.setdefault('note', src)

        # Other optional fields
        if pd.notnull(row.get('Volume')):
            entry['volume'] = str(int(row['Volume']))
        if pd.notnull(row.get('Issue')):
            entry['number'] = str(int(row['Issue']))
        if pd.notnull(row.get('Start Page')) and pd.notnull(row.get('End Page')):
            entry['pages'] = f"{int(row['Start Page'])}-{int(row['End Page'])}"
        if isinstance(row.get('DOI'), str):
            entry['doi'] = row['DOI']

        return entry


    # Read Excel file
    input_path =  os.path.join(input_dir, f"{file_name}.xls")
    excel_file = pd.ExcelFile(input_path)
    if sheet_name is None:
        sheet_name = excel_file.sheet_names[0]  # type: ignore
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Map Document Type to BibTeX entry types
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

    # Build BibTeX database
    database = BibDatabase()
    for _, row in df.iterrows():  # type: ignore
        database.entries.append(row_to_bibtex(row))

    output_path = os.path.join(input_dir, f"{file_name}.bib")
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as bibtex_file:
        bibtexparser.dump(database, bibtex_file)

    print(f"✅ BibTeX file generated: {output_path}")


def merge_bib(bib_file_list: list[str], output_name: str):
    """
    Merge multiple BibTeX files, deduplicate entries by title,
    and keep the most complete entry (with the most non-empty fields).

    - bib_file_list: List[str], paths of .bib files to be merged
    - output_file: str, output BibTeX file path
    """

    removed_count = 0  # Counter for removed/merged duplicates

    def merge_entries(entry_a: dict, entry_b: dict) -> dict:
        """
        Merge two BibTeX entries by taking the union of fields.
        If both entries contain the same field:
        - Prefer the non-empty value
        - If both are non-empty and different, keep the longer one
        """
        nonlocal removed_count
        removed_count += 1  # Each call indicates entry_b is considered a duplicate

        merged = dict(entry_a)
        for k, v in entry_b.items():
            v = str(v).strip()
            if not v:
                continue
            if k not in merged or not merged[k].strip():
                merged[k] = v
            else:
                # If both have values and they differ, keep the longer one
                if merged[k].strip() != v and len(v) > len(merged[k]):
                    merged[k] = v
        return merged

    def normalize_title(title: str) -> str:
        """Normalize title format: remove special quotes, spaces, and case differences."""
        if not title:
            return ''
        t = title.lower().strip()
        t = unicodedata.normalize('NFKC', t)
        t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        return ''.join(ch for ch in t if ch.isalnum() or ch.isspace())  # remove punctuation

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

    merged_database = BibDatabase()
    merged_database.entries = list(title_dict.values()) + no_title_entries

    # Write output file
    output_path = os.path.join(output_dir, f"{output_name}.bib")
    with open(output_path, 'w', encoding='utf-8') as f:
        bibtexparser.dump(merged_database, f)

    total_entries = len(merged_database.entries)
    print(f"Merge completed. Total entries: {total_entries}")
    print(f"Removed/merged duplicate entries: {removed_count}")
 
def bib2csv(output_name: str):
    """
    Import a BibTeX file into Excel format,
    keep only selected columns, and add a column containing the raw BibTeX entry.
    """
    output_path = os.path.join(output_dir, f"{output_name}.bib")
    with open(output_path, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    rows = []
    for entry in bib_database.entries:
        # Manually reconstruct BibTeX string
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
            'BibTeX': bibtex_str  # newly added column
        })

    df = pd.DataFrame(rows)
    csv_file_path = os.path.join(output_dir, f"{output_name}.csv")
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

    print(f"CSV file generated: {csv_file_path}")

def preprocess_all(bib_file_name: str, output_name: str):
    xls2bib(bib_file_name)
    bib_files = ["acm.bib", "ieee.bib", "wiley.bib", f"{bib_file_name}.bib"]
    merge_bib(bib_files, output_name)
    bib2csv(output_name)

if __name__ == "__main__":
    input_name = "wos"
    output_name = "remove_duplication"
    preprocess_all(input_name, output_name)
