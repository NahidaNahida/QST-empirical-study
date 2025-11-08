REM Update source data
python -m private.xlsx2csv

REM Update .bib and .tex
python -m scripts.tex.key_numbers
python -m scripts.tex.bibtex

REM Update results
python -m scripts.results.bib_analysis
python -m scripts.results.rq1_quantum_programs
python -m scripts.results.rq3_scalability_issue
python -m scripts.results.rq10_available_toolings