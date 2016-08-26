from __future__ import unicode_literals
from itertools import groupby
import os

import transaction
from six import text_type
from clld.db.meta import DBSession
import pandas

from clldutils.misc import slug
from json import load as jsonload
from clld.db.models.common import ValueSet, ContributionContributor, Contributor, Language
from clldutils.dsv import reader
from clld.scripts.util import Data
from clld.lib.bibtex import EntryType, FIELDS
from clldutils.dsv import reader
from pycldf.dataset import Dataset
from pycldf.util import MD_SUFFIX

from lexibank.models import (
    LexibankLanguage, Concept, Counterpart, Provider, CounterpartReference,
    LexibankSource, Cognateset, CognatesetCounterpart,
)
from clldclient.glottolog import Glottolog



def load_metadata(path):
    mdpath = path + '-metadata.json'
    assert os.path.exists(mdpath)
    with open(mdpath) as mdfile:
        md = jsonload(mdfile)
    return md

def unique_id(contrib, local_id):
    return '%s-%s' % (contrib.id, local_id)


def cldf2clld(source, contrib, id_):
    name = source.id
    if source.get('author'):
        name = source['author']
    if source.get('year'):
        name += ' %s' % source['year']
    description = source.get('title')
    return LexibankSource(
        id=unique_id(contrib, id_),
        provider=contrib,
        bibtex_type=getattr(EntryType, source.genre, EntryType.misc),
        name=name,
        description=description,
        **{k: v for k, v in source.items() if k in FIELDS})

id = 0
def import_dataset(path, contrib, languoids, conceptsets):
    global id
    values = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    langs = {l.id: l for l in DBSession.query(LexibankLanguage)}

    for i, row in pandas.io.parsers.read_csv(
            path,
            sep="," if path.endswith(".csv") else "\t",
            encoding='utf-16').iterrows():
        id += 1
        if not row['Value'] or not row['Feature_ID']:
            continue

        fid = row['Feature_ID'].split('/')[-1]

        language = langs.get(row['Language_ID'])
        if language is None:
            # Look it up in the metadata table
            lang_id = row['Language_ID']
            gid = (lang_id.split("-")[1]
                   if lang_id.split("-")[0] == "p" else
                   lang_id.split("-")[0])
            try:
                language = LexibankLanguage(
                    id=lang_id,
                    glottolog=gid,
                    name=languoids.loc[lang_id, 'Language name (-dialect)'],
                    latitude=languoids.loc[lang_id, 'Lat'],
                    longitude=languoids.loc[lang_id, 'Lon'])
            # If it's not in there, query glottolog!
            except KeyError:
                try:
                    languoid = glottolog.languoid(gid)
                    language = LexibankLanguage(
                        id=lang_id,
                        glottolog=gid,
                        name=languoid.name,
                        latitude=languoid.latitude,
                        longitude=languoid.longitude)
                except AttributeError:
                    print("Language ID {:s} could not be found in metadata or in glottolog".format(lang_id))
                    continue
                    raise KeyError("Language ID {:s} could not be found in metadata or in glottolog".format(lang_id))
            langs[lang_id] = language

        concept = concepts.get(fid)
        if concept is None:
            try:
                cs = conceptsets.loc[fid]
                concepts[row['Feature_ID']] = concept = Concept(
                    # FIXME: get gloss and description from concepticon!
                    id=fid,
                    name=cs['English'],
                    description=(
                        cs['English']
                        if pandas.isnull(cs['Indonesian']) else
                        '{:s}; Indonesian prompt: {:s}'.format(cs['English'], cs['Indonesian'])),
                    semanticfield=cs['Semantic field'])
            except KeyError:
                cs = fid
                concepts[row['Feature_ID']] = concept = Concept(
                    # FIXME: get gloss and description from concepticon!
                    id=fid, name=fid, description=fid, semanticfield=fid)
                

        vsid = unique_id(contrib, '%s-%s' % (language.id, concept.id))
        vid = unique_id(contrib, str(id))

        vs = values['ValueSet'].get(vsid)
        if vs is None:
            vs = values.add(
                ValueSet, vsid,
                id=vsid,
                parameter=concept,
                language=language,
                contribution=contrib,
                source=None)  # FIXME: add sources!
            
        loan = row.get('Loan', False)
        if pandas.isnull(loan):
            loan = False
        counterpart = values.add(
            Counterpart, str(id),
            id=vid,
            valueset=vs,
            name=row['Value'],
            description=row.get('Comment'),
            context=row.get('Context'),
            variety_name=row.get('Language_name'),
            loan=loan,
        )

        for ref in row.get('References', []):
            CounterpartReference(
                counterpart=counterpart,
                source=sources[ref.source.id],
                description=ref.description)

        if not pandas.isnull(row.get('Cognate Set')):
            cognateset_name = row['Cognate Set'].split(',')[0].strip()
            csid = "{:s}-{:s}".format(concept.id, cognateset_name)
            print("Cognate:", csid)
            cs = Cognateset.get(csid, key='id', default=None)
            if cs is None:
                cs = Cognateset(id=csid,
                                type="manual",
                                name=cognateset_name,
                                contribution=contrib)
            cp = counterpart
            cognate = {}
            DBSession.add(CognatesetCounterpart(
                            cognateset=cs,
                            counterpart=cp,
                            cognate_detection_method=cognate.get('Cognate_detection_method'),
                            alignment=cognate.get('Alignment'),
                            alignment_method=cognate.get('Alignment_method'),
                            doubt=cognate.get('Doubt', False)))
        else:
            print("Cognate: null")

        #for key, src in data['Source'].items():
        #    if key in vs.source:
        #        ValueSetReference(valueset=vs, source=src, key=key)
        DBSession.flush()

    contrib.language = language

def old_import_cldf(srcdir, md, languoids, conceptsets):
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
        for fname in cldfdir.glob('*' + MD_SUFFIX):
            ds = Dataset.from_metadata(fname)
            for src in ds.sources.items():
                if src.id not in sources:
                    sources[src.id] = cldf2clld(src, contrib, len(sources) + 1)
            import_dataset(ds, contrib, languoids, conceptsets, sources, values)
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

def import_cldf(srcdir, conceptsets, languoids):
    for dirpath, dnames, fnames in os.walk(srcdir):
        for fname in fnames:
            if os.path.splitext(fname)[1] in ['.tsv', '.csv']:
                try:
                    md = load_metadata(os.path.join(dirpath, fname))
                    contrib = Provider(
                        id="".join(fname.split('.')[:-1]),
                        name=md.get('dc:title', fname),
                        description=md.get('dc:bibliographicCitation'),
                        url=md.get('dc:identifier'),
                        license=md.get('dc:license'),
                        aboutUrl=md.get('aboutUrl'),
                    )
                    with transaction.manager:
                        import_dataset(os.path.join(dirpath, fname), contrib, languoids, conceptsets)
                        print(os.path.join(dirpath, fname))
                except:
                    print('ERROR')
                    raise
