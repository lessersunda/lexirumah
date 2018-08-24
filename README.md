# Lexibank

Lexibank consists of several pieces:
- The Lexibank dataset format, based on CLDF
- The Lexibank workflow and software: `pylexibank`
- The [Lexibank GitHub organisation](https://github.com/lexibank)
- The [Lexibank ZENODO community](https://zenodo.org/communities/lexibank)


## The Lexibank dataset format

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


### Lexibank data conventions

1. Dataset names should be lowercase and either:
- the database name, if this is what database is well-known as (e.g. "abvd", "asjp" etc), 
- \<author\>\<languagegroup\> (e.g. "grollemundbantu" etc)

2. Cognate sets should be "global" within a dataset e.g. a cognate set '1' will be cognate across all languages and all words. If the cognates for a specific dataset are done "locally" within word-meaning slots (e.g. cognate set '1' for "hand" is different to cognate set '1' for "to fly") then the dataset must label these such that they are globally unique e.g. "hand-1" and "tofly-1".

3. Datasets that require preprocessing with external programs (e.g. antiword, libreoffice) should store intermediate/artifacts in ./raw/ directory, and the `cmd_install` code should install from that rather than requiring an external dependency.


### Attribution

There are multiple levels of contributions to a Lexibank dataset:
- Typically, lexibank datasets are derived from published data (be it supplemental material of a paper or public databases). Attribution to this source dataset is given by specifying its full citation in the dataset's metadata and by adding the source title to the release title of a lexibank dataset.
- Often the source dataset is also an aggregation of data from other sources. If possible, these sources (and the corresponding references) are kept in the lexibank dataset's CLDF; otherwise we refer to the source dataset for a description of its sources.
- Deriving a lexibank dataset from a source dataset involves adding code, mapping to reference catalogs and to some extent also linguistic judgements. These contributions are listed in a dataset's `CONTRIBUTORS.md` and translate to the list of authors of released versions of the lexibank dataset.


### Dataset curation: Versioning and Releases

Lexibank datasets should be versioned using a version control system. If possible, the dataset repositories should
be hosted in a way that allows ["installation" of the dataset using pip](https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support). If a dataset is curated in a repository on GitHub, it may be forked into the [lexibank organisation](https://github.com/lexibank) (see below) as a way of "official" endorsement and to increase its visibility.

If a dataset is under version control, releases should be made using the appropriate functionality of the version
control software to make sure they can be retrieved in a controlled way via installation. Release tags (a.k.a. version numbers) **should** follow [semantic versioning](https://semver.org/) principles, i.e. be of the form `vMAJOR.MINOR.PATCH`. 

In addition (and also when a dataset is not curated via vcs) releases **must** be deposited on ZENODO for longterm archiving and public accessibility via DOI. Published datasets on ZENODO **should** be submitted to the 
[lexibank community](https://zenodo.org/communities/lexibank). If a dataset is derived from a source dataset, attribution to this source **must** be given in the release description.

**Notes:** 
- When datasets are curated on GitHub and hooked up to ZENODO to trigger automatic deposits of releases, the release tag **must** start with a letter (otherwise the deposit will fail).
- Additional tags can be added to add context - e.g. when a release is triggered by a specific use case (for example the CLICS 2.0 release). This can be done using `git` as follows:
  ```bash
  git checkout tags/vX.Y.Z
  git tag -a "clics-2.0"
  git push origin --tags
  ```


## The Lexibank workflow and `pylexibank`

TODO


## The Lexibank organisation on GitHub

The Lexibank organisation on GitHub has the following purposes:

- It hosts the `lexibank/lexibank` repository, used for Lexibank documentation and policy making.
- It hosts the `lexibank/pylexibank` repository, used to maintain the `pylexibank` package.
- It hosts Lexibank dataset repositories curated by members of the Lexibank org.
- It may host [**forks**](https://en.wikipedia.org/wiki/Fork_(software_development)) of Lexibank dataset repositories curated elsewhere on GitHub. Such forks are not meant as starting points for derived works, but as
endorsements of the original datasets. Releases from these forks **must** only be made if the original dataset is
abandoned (and its license allows [derivative works](https://en.wikipedia.org/wiki/Derivative_work)).



## The Lexibank community on ZENODO

GitHub is not a viable platform for longterm (or even midterm) preservation of Lexibank datasets. However, it provides an excellent collaborative curation platform, and can easily be hooked up with ZENODO, thereby providing longterm preservation for released versions of datasets.

To establish a "corporate identity" of Lexibank datasets on ZENODO, such datasets **should** be submitted to the [lexibank ZENODO community](https://zenodo.org/communities/lexibank). We also recommend the keywords "CLDF" for Lexibank datasets on ZENODO.
