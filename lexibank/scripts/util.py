
import os

from nameparser import HumanName
import transaction
import pandas

from clldutils.misc import slug
from json import load as jsonload
from clld.db.meta import DBSession
from clld.db.models.common import ValueSet, ContributionContributor, Contributor, Language
from clldutils.dsv import reader
from clld.scripts.util import Data

from clldclient.glottolog import Glottolog

from lexibank.models import LexibankLanguage, Concept, Counterpart, Wordlist, Cognateset


def import_dataset(path, concept_table, languages):
    # look for metadata
    # look for sources
    # then loop over values
    dirpath, fname = os.path.split(path)
    basename, ext = os.path.splitext(fname)
    glottolog = Glottolog()

    mdpath = path + '-metadata.json'
    assert os.path.exists(mdpath)
    with open(mdpath) as mdfile:
        md = jsonload(mdfile)
    md = md['properties']

    cname = md['name']
    if 'id' in md:
        cname = '%s [%s]' % (cname, md['id'])
    contrib = Wordlist(id=basename, name=cname)
    contributors = md.get('typedby', md.get('contributors'))

    if contributors:
        contributor_name = HumanName(contributors)
        contributor_id = slug(contributor_name.last + contributor_name.first)
        contributor = Contributor.get(contributor_id, default=None)
        if not contributor:
            contributor = Contributor(id=contributor_id, name='%s' % contributor_name)

        DBSession.add(
            ContributionContributor(contribution=contrib, contributor=contributor))

    #bibpath = os.path.join(dirpath, basename + '.bib')
    #if os.path.exists(bibpath):
    #    for rec in Database.from_file(bibpath):
    #        if rec['key'] not in data['Source']:
    #            data.add(Source, rec['key'], _obj=bibtex2source(rec))

    data = Data()
    concepts = {p.id: p for p in DBSession.query(Concept)}
    language = None

    for i, row in pandas.io.parsers.read_csv(
            path,
            sep="," if path.endswith(".csv") else "\t",
            encoding='utf-16').iterrows():
        if not row['Value'] or not row['Feature_ID']:
            continue

        fid = row['Feature_ID'].split('/')[-1]
        vsid = '%s-%s-%s' % (basename, row['Language_ID'], fid)
        vid = '%s-%s' % (basename, i + 1)

        language = Language.get(row['Language_ID'], default=None)
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
                    name=languages.loc[lang_id, 'Language name (-dialect)'],
                    latitude=languages.loc[lang_id, 'Lat'],
                    longitude=languages.loc[lang_id, 'Lon'])
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
                
        try:
            parameter = concepts[fid]
        except KeyError:
            try:
                concepts[fid] = parameter = Concept(
                    id=fid,
                    name=concept_table.loc[fid, "English"],
                )
            except KeyError:
                print(fid, concept_table.index)
                concepts[fid] = parameter = Concept(
                    id=fid,
                    name=fid,
                )
                

        vs = data['ValueSet'].get(vsid)
        if vs is None:
            vs = data.add(
                ValueSet, vsid,
                id=vsid,
                parameter=parameter,
                language=language,
                contribution=contrib,
                source=row.get('Source'))

        counterpart = Counterpart(
            id=vid,
            valueset=vs,
            name=row['Value'],
            description=row.get('Comment'),
            loan=row.get('Loan') == 'yes')

        if not pandas.isnull(row.get('Cognate Set')):
            csid = row['Cognate Set'].split(',')[0].strip()
            print("Cognate:", csid)
            cs = Cognateset.get(csid, key='name', default=None)
            if cs is None:
                cs = Cognateset(name=csid)
            counterpart.cognateset = cs
        else:
            print("Cognate: null")

        #for key, src in data['Source'].items():
        #    if key in vs.source:
        #        ValueSetReference(valueset=vs, source=src, key=key)
        DBSession.flush()

    contrib.language = language


def import_cldf(srcdir, concepts, languages):
    for dirpath, dnames, fnames in os.walk(srcdir):
        for fname in fnames:
            if os.path.splitext(fname)[1] in ['.tsv', '.csv']:
                try:
                    with transaction.manager:
                        import_dataset(os.path.join(dirpath, fname), concepts, languages)
                        print(os.path.join(dirpath, fname))
                except:
                    print('ERROR')
                    raise
