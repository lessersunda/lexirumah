### The anatomy of a Lexibank dataset

A Lexibank dataset conists of the following directories and files:

- `README.md` provides basic metadata of the dataset in human readable form, in particular 
  - a bibliographic citation
  - license information
  - quality assessment and usage info

  **Note:** For datasets curated via `pylexibank` this file is automatically (re-)created.
- `LICENSE` - the license under which the dataset is available.

  **Note:** For datasets curated via `pylexibank` this file is automatically (re-)created.
- `CONTRIBUTORS.md` lists contributions - other than the original data - to the lexibank dataset, marking the responsible maintainer with the role `maintainer`.
- `metadata.json` provides - hand curated - basic metadata of a dataset to be used by applications like `pylexibank` for automated curation.
- `setup.py` turns the repository into a lightweight python package, making it installable via `pip install -e git+https://github.com/...`
- `test.py` makes consistency checks runnable with `pytest`
- `.travis.yml` hooks up `test.py` with Travis-CI for continuous consistency checks.
- `lexibank.json` stores metadata read and written by `pylexibank` within the curation workflow.
- `raw/` stores data as provided at the original source.

  **Note:** For datasets curated via `pylexibank` this directory may be populated automatically when the `download` command is run.
- `etc/`<a id="etc"> </a> stores supplemental data used for the conversion to a CLDF dataset. As opposed to the data in `raw/` this is typically contributed by the repository maintainers as listed in `CONTRIBUTORS.md`. The following files are recognized by `pylexibank.Dataset`:
  - `orthography.tsv`: an orthography profile (Cysouw and Moran 2018) used to segment the forms in the dataset.
  - `languages.csv`: a CSV file conforming to the specification for a [CLDF `LanguageTable`](https://github.com/cldf/cldf/tree/master/components/languages). This file is used to supplement language metadata that is lacking in the source dataset, in particular a Glottocode.
  - `concepts.csv`: a CSV file (optionally TAB-separated, indicated by a `.tsv` suffix) according to the specification of a Concepticon concept list, i.e. with - minimally - columns `NUMBER` (a local ID), `CONCEPTICON_ID` (the ID of the corresponding Concepticon concept set), `GLOSS` (the gloss for the concept used in the dataset). For datasets which have not been collected by following an established concept list, this file is supposed to be submitted for inclusion into Concepticon upon release of the dataset. Once accepted into Concepticon, `concepts.csv` can be replaced by adding the Concepticon concept list ID to `metadata.json`.
  - `lexemes.csv`: A CSV file serving as list of errata to correct lexemes in the source dataset when creating the CLDF data. While the orthography profile can "fix" segment-level inconsistencies of transcriptions, `lexemes.csv` should be used for wholesale replacement, e.g. to remove inline comments, or additions like spelling variants. Thus, of the two columns `LEXEME` and `REPLACEMENT` the first should match a lexeme in the source dataset and the second should list the replacement to use when adding lexemes to the CLDF dataset.
- `cldf/` contains the data of the dataset as CLDF Wordlist.

**TODO**: `pylexibank` provides a command to create the skeleton of a new lexibank dataset.
