REM Update source data
python -m private.xlsx2csv

REM Update .bib and .tex
python -m scripts.tex.key_numbers
python -m scripts.tex.bibtex

REM Update results
python -m scripts.results.bib_analysis
python -m scripts.results.rq1
python -m scripts.results.rq3
python -m scripts.results.rq4
python -m scripts.results.rq6
python -m scripts.results.rq8
python -m scripts.results.rq9
python -m scripts.results.rq10