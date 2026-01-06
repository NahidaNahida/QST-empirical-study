# QST-empirical-study
This repository includes the data, documentation, and code for our article entitled *A Methodological Analysis of Empirical Studies in Quantum Software Testing*. This article systematically conducts a methodological analysis of empirical studies in quantum software testing based on a pool of 59 primary studies.

Long-term archive in Zenodo:

+ Badge: [![DOI](https://zenodo.org/badge/1076040404.svg)](https://doi.org/10.5281/zenodo.18159892)
+ Link: [https://doi.org/10.5281/zenodo.18159892](https://doi.org/10.5281/zenodo.18159892)

## Data and Documentation

### Raw Data for Systematic Literature Review

Our research methodology is based on a systematic literature review. Herein, we record the original literature collected from available digital databases and the manually annotated metadata for further analysis of research questions.

+ [`literature_pool`](./doc/literature_pool): We include the original literature through a keyword search in [`raw`](./doc/literature_pool/raw). The deduplicated literature pool is provided in [`merged`](./doc/literature_pool/merged).
+ [`annotated_data`](./doc/annotated_data): This file [`final_list.csv`](./doc/annotated_data/final_list.csv) contains all the metadata with human annotation, where our discussions for bibliometric analysis and each research question completely rely on this file. Also, we document the candidate literature introduced from the keyword search and the snowballing search. 

### Generated Data

All the generated data are preserved in the folder [`build`](`./build`). It is worth noting that: the folder [`figures`](./build/figures) incorporates all the generated figures in the PDF format used in the main body of our article, and the folder [`tables`](./build/tables) contains all the generated LaTeX code that can be compiled to the tables displayed in our article.

## Code

We provide the source code to generate the figures and tables mentioned above. 

### Getting Started

1. Use the following command to clone this repository.

   ```bat
   git clone https://github.com/NahidaNahida/QST-empirical-study.git
   ```

2. Create a virtual Conda environment.

   ```bat
   conda create --name qst_empirical python=3.11.13
   ```

3. Activate the environment.

   ```bat
   conda activate qst_empirical
   ```

4. Upon changing the directory to `QST-empirical-study`, download the required packages based on [requirements.txt](./requirements.txt).

   ```bat
   conda install --file requirements.txt
   ```

Now, it is ready to run our code.

### Implementation

We provide a `.bat` file to reproduce the results of the bibliometric analysis and the ten research questions within one batch, by running the following command:

```bat
./run.bat
```

The corresponding source codes are offered in [`results`](./scripts/results).
