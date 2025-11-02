REM Update source data
python -m private.xlsx2csv

REM Update .bib and .tex
python -m src.key_numbers
python -m src.bibtex