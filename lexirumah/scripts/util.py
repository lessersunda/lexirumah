from __future__ import unicode_literals
from itertools import groupby

import transaction
from six import text_type
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet
from clld.lib.bibtex import EntryType, FIELDS
from csvw.dsv import reader
from pycldf.dataset import Dataset
from tqdm import tqdm

from lexirumah.models import (
    LexiRumahLanguage, Concept, Counterpart, Provider, CounterpartReference,
    LexiRumahSource, Cognateset, CognatesetCounterpart,
)
import re
import math
import collections

import csv
import json

import sys
import argparse

from clldutils.path import Path
from pycldf.sources import Source
from pycldf.dataset import Wordlist, Dataset
from csvw.metadata import Column

from urllib.error import HTTPError
from urllib.request import urlopen

import newick
from pybtex.database import BibliographyData, Entry
try:
    import pyglottolog
    local_glottolog = pyglottolog.Glottolog()
except (ValueError, ImportError):
    local_glottolog = None


def unique_id(contrib, local_id):
    return '%s-%s' % (contrib.id, local_id)


def cldf2clld(source, contrib, id_):
    name = source.id
    if source.get('author'):
        name = source['author']
    if source.get('year'):
        name += ' %s' % source['year']
    description = source.get('title')
    return LexiRumahSource(
        id=unique_id(contrib, id_),
        provider=contrib,
        bibtex_type=getattr(EntryType, source.genre, EntryType.misc),
        name=name,
        description=description,
        **{k: v for k, v in source.items() if k in FIELDS and k not in ['institution']})


def import_dataset(ds, contrib, languoids, conceptsets, sources, values):
    data = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    langs = {l.id: l for l in DBSession.query(LexiRumahLanguage)}

    for i, row in enumerate(ds.rows):
        if not row['Value'] or not row['Parameter_ID'] or not row['Language_ID']:
            continue

        lid = row['Language_ID'].lower()
        if lid == 'none':
            continue

        if not row['Parameter_ID'].strip():
            continue

        language = langs.get(lid)
        if language is None:
            languoid = languoids.get(lid)
            if not languoid:
                continue
            langs[lid] = language = LexiRumahLanguage(
                id=lid,
                name=languoid.name,
                level=text_type(languoid.level.name),
                latitude=languoid.latitude if languoid.id != 'plau1238' else -10,
                longitude=languoid.longitude)

        concept = concepts.get(row['Parameter_ID'])
        if concept is None:
            cs = conceptsets[row['Parameter_ID']]
            concepts[row['Parameter_ID']] = concept = Concept(
                id=row['Parameter_ID'],
                name=cs.gloss,
                description=cs.definition,
                semanticfield=cs.semanticfield)

        vsid = unique_id(contrib, '%s-%s-%s' % (ds.name, language.id, concept.id))
        vid = unique_id(contrib, row['ID'])

        vs = data['ValueSet'].get(vsid)
        if vs is None:
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=concept,
                language=language,
                contribution=contrib,
                source=None)  # FIXME: add sources!

        counterpart = values.add(
            Counterpart, row['ID'],
            id=vid,
            valueset=vs,
            name=row['Form'],
            description=row.get('Comment'),
            context=row['Value'],
            variety_name=row.get('Language_name'),
            loan=row.get('Loan', False),
        )

        for ref in row.refs:
            CounterpartReference(
                counterpart=counterpart,
                source=sources[ref.source.id],
                description=ref.description)


def import_cldf(srcdir, md, languoids, conceptsets):
    with transaction.manager:
        contrib = Provider(
            id=srcdir.name,
            name=md['dc:title'],
            description=md.get('dc:bibliographicCitation'),
            url=md.get('dc:identifier'),
            license=md.get('dc:license'),
            aboutUrl=md.get('aboutUrl'),
        )
        DBSession.add(contrib)
        sources = {}
        cldfdir = srcdir.joinpath('cldf')
        values = Data()
        for fname in tqdm(list(cldfdir.glob('*' + MD_SUFFIX)), leave=False):
            ds = Dataset.from_metadata(fname)
            for src in ds.sources.items():
                if src.id not in sources:
                    sources[src.id] = cldf2clld(src, contrib, len(sources) + 1)
            import_dataset(ds, contrib, languoids, conceptsets, sources, values)
            DBSession.flush()
        # import cognates:
        if cldfdir.joinpath('cognates.csv').exists():
            for csid, cognates in groupby(
                    reader(cldfdir.joinpath('cognates.csv'), dicts=True),
                    lambda i: i['Cognate_set_ID']):
                cs = Cognateset(id=unique_id(contrib, csid), contribution=contrib)
                for cognate in cognates:
                    cp = values['Counterpart'].get(cognate['Word_ID'])
                    if cp:
                        DBSession.add(CognatesetCounterpart(
                            cognateset=cs,
                            counterpart=cp,
                            cognate_detection_method=cognate['Cognate_detection_method'],
                            alignment=cognate['Alignment'],
                            alignment_method=cognate['Alignment_method'],
                            doubt=cognate['Doubt'] == 'True'))

REPLACE = {
    " ": "_",
    '’': "'",
    '-': "_",
    '.': "_",
    "'": "'",
    "*": "",
    '´': "'",
    'µ': "_",
    'ǎ': "a",
    '̃': "_",
    ',': "ˌ",
    '=': "_",
    '?': "ʔ",
    'ā': "aː",
    "ä": "a",
    'Ɂ': "ʔ",
    "h̥": "h",
    "''": "'",
    "á": "'a",
    'ū': "uː",
}


def identifier(string):
    """Turn a string into a python identifier."""
    return re.sub('(\W|^(?=\d))+', '_', string).strip("_")


def resolve_brackets(string):
    """Resolve a string into all description without brackets

    For a `string` with matching parentheses, but without nested parentheses,
    yield every combination of the contents of any parenthesis being present or
    absent.

    >>> list(resolve_brackets("no brackets"))
    ["no brackets"]

    >>> sorted(list(resolve_brackets("(no )bracket(s)")))
    ["bracket", "brackets", "no bracket", "no brackets"]

    """
    if "(" in string:
        opening = string.index("(")
        closing = string.index(")")
        for form in resolve_brackets(string[:opening] + string[closing+1:]):
            yield form
        for form in resolve_brackets(string[:opening] + string[opening+1:closing] + string[closing+1:]):
            yield form
    else:
        yield string


def online_languoid(iso_or_glottocode):
    """Look the glottocode or ISO-639-3 code up in glottolog online.

    Return a Namespace object with attributes corresponding to the JSON API
    dictionary keys. Return None if the code is invalid, no matter whether it
    is well-formatted (but unused) or not.

    Parameters
    ----------
    iso_or_glottocode: str
        A three-letter ISO-639-3 language identifier or a four-letter-four-digit
        Glottolog language identifier.

    Returns
    -------
    Namespace or None

    """
    if re.fullmatch("[a-z]{3}", iso_or_glottocode):
        try:
            data = json.loads(urlopen(
                "http://glottolog.org/resource/languoid/iso/{:}.json".format(
                    iso_or_glottocode)
            ).read().decode('utf-8'))
        except HTTPError:
            return None
    elif re.fullmatch("[a-z]{4}[0-9]{4}", iso_or_glottocode):
        try:
            data = json.loads(urlopen(
                "http://glottolog.org/resource/languoid/id/{:}.json".format(
                    iso_or_glottocode)
            ).read().decode('utf-8'))
        except HTTPError:
            return None
    else:
        return None
    language = argparse.Namespace()
    for key, val in data.items():
        setattr(language, key, val)
    return language


def languoid(iso_or_glottocode):
    """Look the glottocode or ISO-639-3 code up in glottolog.

    If a local installation of Glottolog is available through
    `pyglottolog.Glottolog()`, use that; otherwise resort to Glottolog online.
    Return a Namespace object with attributes corresponding to the JSON API
    dictionary keys. Return None if the code is invalid, no matter whether it
    is well-formatted (but unused) or not.

    Parameters
    ----------
    iso_or_glottocode: str
        A three-letter ISO-639-3 language identifier or a four-letter-four-digit
        Glottolog language identifier.

    Returns
    -------
    Namespace or None

    """
    if local_glottolog:
        language = local_glottolog.languoids_by_code().get(
            iso_or_glottocode)
        return language
    else:
        return online_languoid(iso_or_glottocode)


def clade_codes(glottolog_language):
    """Generate the set of all glottocodes in the clade.

    Given a Glottolog languoid object, iterate recursively through all
    children, adding their glottocodes to a set.

    Parameters
    ----------
    glottolog_language: pyglottolog.languoid.Languoid
        A glottolog languoid, ancestor of all languoids in a clade.

    Returns
    -------
    Set of str

    """
    all_codes = {glottolog_language.glottocode}
    for child in glottolog_language.children:
        all_codes |= clade_codes(child)
    return all_codes


def lexirumah_glottocodes(dataset=None, result={}):
    """Generate a dict associating LexiRumah IDs with Glottolog objects

    Returns
    -------
    Dict of Str: Str

    """
    if dataset is None:
        dataset = get_dataset()
    if result != {}:
        return result
    for lect in dataset["LanguageTable"].iterdicts():
        g = None
        try:
            g = lect["Glottocode"]
        except KeyError:
            pass
        if g is None:
            g = re.match("[a-z]{4}[0-9]{4}", lect["ID"]).group()
        result[lect["ID"]] = languoid(g)
    return result


def glottolog_clade(iso_or_glottocode, dataset=None):
    """List all LexiRumah lects belonging to a Glottolog clade.

    Return a list of all LexiRumah lect IDs that belong to a glottolog clade
    specified by Glottocode or ISO-639-3 code.

    Parameters
    ----------
    iso_or_glottocode: str
        A three-letter ISO-639-3 language identifier or a four-letter-four-digit
        Glottolog language identifier.

    Returns
    -------
    List of str

    """
    if dataset is None:
        glottocodes = lexirumah_glottocodes()
    else:
        glottocodes = lexirumah_glottocodes(dataset, {})

    clade_id = languoid(iso_or_glottocode).id

    clade = set()
    for local_id, lect in glottocodes.items():
        for parent in lect.classification:
            if parent["id"] == clade_id:
                clade.add(local_id)
                break
    return clade


def all_lects(dataset=None):
    if dataset is None:
        datase = get_dataset(Path(__file__).parent.parent /
                "cldf" / "Wordlist-metadata.json")


def cognate_sets(dataset, code_column=None, partial_cognates="exact"):
    """Load cognate codes from a CLDF.

    The distinction is made depending on the file extension: `.json` files are
    loaded as metadata descriptions, all other files are matched against the
    CLDF module specifications. Directories are checked for the presence of
    any CLDF datasets in undefined order of the dataset types.

    Partial cognate codes are handled differently depending on the value of
    partial_cognates: "exact" (the default) or "intersection". A form with
    partial cognate classes '1 2' will be listed under class (1, 2) in "exact"
    mode and under both classes 1 and 2 in "intersection" mode.

    Parameters
    ----------
    dataset : pycldf.Wordlist
        CLDF Wordlist data set
    code_column : str
        The name of the column containing the cognate codes in the FormTable
        (default: check FormTable and CognateTable for a cognatesetReference)
    partial_cognates : {"exact", "intersection"}
        Partial cognates handling mode
        (default: "exact")

    Returns
    -------
    dict mapping Cognateset IDs to sets of Form IDs

    """
    data = collections.defaultdict(lambda: set())
    if code_column:
        cognate_column_in_form_table = True
    else:
        try:
            code_column = dataset["FormTable", "cognatesetReference"].name
            cognate_column_in_form_table = True
            # The form table contains cognate sets!
        except KeyError:
            cognatesets = collections.defaultdict(lambda: "?")
            try:
                form_reference = dataset["CognateTable", "formReference"].name
                code_column = dataset["CognateTable", "cognatesetReference"].name
            except KeyError:
                raise ValueError(
                    "Dataset {:} has no cognatesetReference column in its "
                    "primary table or in a separate cognate table. "
                    "Is this a metadata-free wordlist and you forgot to "
                    "specify code_column explicitly?".format(filename))
            for row in dataset["CognateTable"].iterdicts():
                cognatesets[row[form_reference]] = row[code_column]
            cognate_column_in_form_table = False

    form_column = dataset["FormTable", "id"].name

    if cognate_column_in_form_table:
        for row in dataset["FormTable"].iterdicts():
            if partial_cognates == "exact":
                try:
                    data[tuple(row[code_column])].add(row[form_column])
                except TypeError:
                    data[row[code_column]].add(row[form_column])
            else:
                for pcognateset in row[code_column]:
                    data[pcognateset].add(row[form_column])
    else:
        for form, cognateset in cognatesets.items():
            if partial_cognates == "exact":
                try:
                    data[tuple(cognateset)].add(form)
                except TypeError:
                    data[cognateset].add(form)
            else:
                for pcognateset in cognateset:
                    data[pcognateset].add(form)
    return data
