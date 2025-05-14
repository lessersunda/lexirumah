import argparse
import collections
import itertools
import json
import math
import os
import pathlib
import re
import sys

import pycldf
import transaction
from cldfcatalog import Repository
from cldfzenodo.oai import iter_records
from clld.cliutil import Data, bibtex2source

from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.bibtex import EntryType
from clld.scripts.util import parsed_args
from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.util import load_families
from clldutils.jsonlib import load
from clldutils.path import Path, git_describe
from csvw.dsv import reader
from nameparser import HumanName
from pycldf import Dataset
from pycldf.db import Database
from pyclts import CLTS
from pyclts.models import Sound

import lexirumah
from lexirumah.models import (
    Cognateset,
    CognatesetCounterpart,
    CognatesetCounterpartReference,
    Concept,
)
from lexirumah.models import Counterpart
from lexirumah.models import Counterpart as Form
from lexirumah.models import (
    CounterpartReference,
    LexiRumahLanguage,
    LexiRumahSource,
    Provider,
)

from .util import identifier

Dataset = common.Dataset
Editor = common.Editor
Contributor = common.Contributor
ContributionContributor = common.ContributionContributor
ValueSet = common.ValueSet
Identifier = common.Identifier
LanguageIdentifier = common.LanguageIdentifier
model_is_available = True


CLICS_LIST = pathlib.Path(
    "/home/robert/projects/concepticon/concepticon-cldf/raw/"
    "concepticon-data/concepticondata/conceptlists/Rzymski-2020-1624.tsv"
)


def get_dataset(fname: str = "Wordlist-metadata.json"):
    """Load a CLDF dataset.

    Load the file as `json` CLDF metadata description file, or as metadata-free
    dataset contained in a single csv file.

    The distinction is made depending on the file extension: `.json` files are
    loaded as metadata descriptions, all other files are matched against the
    CLDF module specifications. Directories are checked for the presence of
    any CLDF datasets in undefined order of the dataset types.

    Parameters
    ----------
    fname : str or Path
        Path to a CLDF dataset

    Returns
    -------
    pycldf.Dataset
    """
    fname = Path(fname)
    if not fname.exists():
        raise FileNotFoundError("{:} does not exist".format(fname))
    if fname.suffix == ".json":
        return Dataset.from_metadata(fname)
    return Dataset.from_data(fname)


def iter_rows(db, table, query, params=None):
    with db.connection() as conn:
        cu = conn.cursor()
        cu.execute("select * from  {} limit 1".format(table))
        cols = [r[0] for r in cu.description]

    for row in db.query(query, params or ()):
        yield dict(zip(cols, row))


def init_main(args):
    bipa = CLTS(pathlib.Path("/home/robert/projects/cldf-clts/clts-data")).bipa

    cldf = args.cldf
    db = Database(cldf, fname=cldf.directory / ".." / "lexirumah.sqlite")
    clusters = {
        row["CONCEPTICON_ID"]: row
        for row in reader(CLICS_LIST, delimiter="\t", dicts=True)
    }

    zenodo = {rec.doi: rec for rec in iter_records("lexirumah")}
    c2con = {}

    with transaction.manager:
        data = Data()
        dataset = common.Dataset(
            id=lexirumah.__name__,
            name="LexiRumah",
            publisher_name="Leiden University Centre for Linguistics",
            publisher_place="Leiden",
            publisher_url="http://https://www.universiteitleiden.nl/en/humanities/leiden-university-centre-for-linguistics",
            license="http://creativecommons.org/licenses/by/4.0/",
            domain="lexisunda.leiden.edu",
            contact="g.a.kaiping@hum.leidenuniv.nl",
            jsondata={
                "license_icon": "cc-by.png",
                "license_name": "Creative Commons Attribution 4.0 International License",
            },
        )
        DBSession.add(dataset)

        for i, name in enumerate(
            [
                "Owen Edwards",
                "Gereon A. Kaiping",
                "Marian Klamer",
            ],
            start=1,
        ):
            n = HumanName(name)
            c = data.add(common.Contributor, n.last, id=n.last, name=name)
            DBSession.add(common.Editor(contributor=c, dataset=dataset, ord=i))

        contribs = {
            row["Source"]: row
            for row in reader(
                cldf.directory / ".." / "etc" / "lexirumah-bliss.tsv",
                delimiter="\t",
                dicts=True,
            )
        }
        for c in contribs.values():
            assert c["Zenodo"] in zenodo, "DOI: {}".format(c)
            assert zenodo[c["Zenodo"]].version == c["Version"], "Version: {}".format(c)
            c["Title"] = zenodo[c["Zenodo"]].title

        profiles = collections.defaultdict(dict)

        for row in db.query(
            "select distinct sourcetable_id from formtable_sourcetable"
        ):
            contrib = contribs[row[0]]
            d = cldf.directory / ".." / "raw" / contrib["ID"]
            assert d.exists()
            assert contrib["Version"] == git_describe(d), "{} {} {}".format(
                contrib["ID"], contrib["Version"], git_describe(d)
            )

            for p in d.joinpath("etc").glob("orthography"):
                if p.is_dir():
                    for pp in p.glob("*.tsv"):
                        profiles[row[0]][pp.stem] = "{}/{}".format(p.name, pp.name)
            global_profile = d / "etc" / "orthography.tsv"
            if global_profile.exists():
                profiles[row[0]][None] = global_profile.name

            src = cldf.sources[row[0]]
            try:
                src.genre = EntryType.get(src.genre)
            except ValueError:
                src.genre = EntryType.misc
            source = data.add(common.Source, row[0], _obj=bibtex2source(src))
            md = load(d / "metadata.json")
            data.add(
                LexiRumahDataset,
                row[0],
                id=contrib["ID"],
                name=contrib["Title"],
                url=Repository(d).url,
                version=contrib["Version"],
                doi=contrib["Zenodo"],
                source=source,
                jsondata=dict(
                    conceptlists=(
                        [md["conceptlist"]]
                        if isinstance(md["conceptlist"], str)
                        else md["conceptlist"]
                    )
                ),
            )

        l2ds = {
            row[0]: row[1]
            for row in db.query(
                "select distinct f.cldf_languagereference, s.sourcetable_id from formtable as f, formtable_sourcetable as s where s.formtable_cldf_id = f.cldf_id;"
            )
        }

        for row in iter_rows(
            db,
            "languagetable",
            "select l.* from languagetable as l where l.cldf_id in (select cldf_languagereference from formtable)",
        ):
            data.add(
                LexiRumahLanguage,
                row["cldf_id"],
                id=row["cldf_id"],
                name=row["cldf_name"],
                contribution=data["LexiRumahDataset"][l2ds[row["cldf_id"]]],
                latitude=row["cldf_latitude"],
                longitude=row["cldf_longitude"],
                glottocode=row["cldf_glottocode"],
            )

        for row in cldf.iter_rows("ParameterTable"):
            c2con[row["ID"]] = row["Concepticon_ID"]
            cluster = clusters.get(row["Concepticon_ID"])
            data.add(
                Concept,
                row["ID"],
                id=row["Concepticon_ID"],
                name=row["Name"],
                cluster_id=cluster["COMMUNITY"] if cluster else None,
                central_concept=(
                    (cluster["CENTRAL_CONCEPT"] or None) if cluster else None
                ),
            )

        DBSession.flush()
        for key in data:
            data[key] = {k: v.pk for k, v in data[key].items()}

    segments = collections.defaultdict(collections.Counter)
    sounds = {}
    concepts = collections.defaultdict(
        lambda: dict(nwords=0, datasets=set(), languages=set())
    )
    for src in data["Source"]:
        with transaction.manager:
            vss = Data()
            print("{} ...".format(src))
            dscids, dsnwords = set(), 0
            for nlangs, (lid, rows) in enumerate(
                itertools.groupby(
                    iter_rows(
                        db,
                        "formtable",
                        "select f.* from formtable as f, formtable_sourcetable as s "
                        "where s.formtable_cldf_id = f.cldf_id and s.sourcetable_id = ? order by f.cldf_languageReference",
                        (src,),
                    ),
                    lambda r: r["cldf_languageReference"],
                ),
                start=1,
            ):
                cids = set()
                for nwords, row in enumerate(rows, start=1):
                    cid = row["cldf_parameterReference"]
                    concepts[cid]["nwords"] += 1
                    concepts[cid]["datasets"].add(src)
                    concepts[cid]["languages"].add(lid)
                    cids.add(cid)
                    vsid = (src, lid, cid)
                    vs = vss["ValueSet"].get(vsid)
                    if not vs:
                        vs = vss.add(
                            common.ValueSet,
                            vsid,
                            id="{}-{}-{}".format(*vsid),
                            language_pk=data["LexiRumahLanguage"][lid],
                            parameter_pk=data["Concept"][cid],
                            contribution_pk=data["LexiRumahDataset"][src],
                        )
                    profile = None
                    if lid.split("-")[1] in profiles[src]:
                        profile = profiles[src][lid.split("-")[1]]
                    elif None in profiles[src]:
                        profile = profiles[src][None]
                    for s in row["cldf_segments"].split():
                        sound = bipa[s]
                        if isinstance(sound, Sound):
                            sounds[s] = sound.name
                            segments[lid].update([str(sound)])
                    DBSession.add(
                        Form(
                            id=row["cldf_id"],
                            name=row["cldf_form"],
                            segments=row["cldf_segments"],
                            profile=profile,
                            CV_Template=row["CV_Template"],
                            Prosodic_String=row["Prosodic_String"],
                            Dolgo_Sound_Classes=row["Dolgo_Sound_Classes"],
                            SCA_Sound_Classes=row["SCA_Sound_Classes"],
                            valueset=vs,
                        )
                    )
                lang = LexiRumahLanguage.get(lid)
                lang.nwords = nwords
                lang.nconcepts = len(cids)
                dscids |= cids
                dsnwords += nwords
            ds = LexiRumahDataset.get(data["LexiRumahDataset"][src])
            ds.nwords = dsnwords
            ds.nlangs = nlangs
            ds.nconcepts = len(dscids)

    with transaction.manager:
        for cid, data in concepts.items():
            c = Concept.get(c2con[cid])
            c.nwords = data["nwords"]
            c.ndatasets = len(data["datasets"])
            c.nlangs = len(data["languages"])

        for lid, segs in segments.items():
            common.Language.get(lid).jsondata = dict(inventory=segs)

        glottolog_repos = Path(lexirumah.__file__).parent.parent.parent.parent.joinpath(
            "glottolog", "glottolog"
        )
        load_families(
            Data(),
            [(l.glottocode, l) for l in DBSession.query(LexiRumahLanguage)],
            glottolog_repos=glottolog_repos,
            strict=False,
            isolates_icon="tcccccc",
        )
        DBSession.add(common.Config(key="bipa_mapping", jsondata=sounds))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    concept_labels = {
        r[0]: r[1] for r in DBSession.query(common.Parameter.pk, common.Parameter.name)
    }
    for cogset in DBSession.query(Cognateset).options(
        joinedload(Cognateset.counterparts)
        .joinedload(CognatesetCounterpart.counterpart)
        .joinedload(common.Value.valueset)
    ):
        concepts = set()
        for cp in cogset.counterparts:
            concepts.add(cp.counterpart.valueset.parameter_pk)
        cogset.name = "[{:}] (‘{:}’)".format(
            cogset.name, "’/‘".join(sorted([concept_labels[pk] for pk in concepts]))
        )
        cogset.representation = len(cogset.counterparts)
        source_cache = set()
        for rel in cogset.counterparts:
            for source in rel.sources:
                try:
                    links.add(link(self.dt.req, source, **self.get_attrs(source)))
                except AssertionError:
                    links.add(str(source))
        cogset.source_cache = "; ".join(source_cache)

    for concept in DBSession.query(Concept):
        concept.representation = (
            DBSession.query(common.Language)
            .join(common.ValueSet)
            .filter(common.ValueSet.parameter_pk == concept.pk)
            .distinct()
            .count()
        )

    for prov in DBSession.query(Provider):
        q = (
            DBSession.query(common.ValueSet.language_pk)
            .filter(common.ValueSet.contribution_pk == prov.pk)
            .distinct()
        )
        prov.language_count = q.count()
        prov.update_jsondata(language_pks=[r[0] for r in q])

        prov.parameter_count = (
            DBSession.query(common.ValueSet.parameter_pk)
            .filter(common.ValueSet.contribution_pk == prov.pk)
            .distinct()
            .count()
        )
        prov.lexeme_count = (
            DBSession.query(common.Value.pk)
            .join(common.ValueSet)
            .filter(common.ValueSet.contribution_pk == prov.pk)
            .count()
        )

        syns = defaultdict(dict)
        vs = common.ValueSet.__table__
        cp = Counterpart.__table__
        v = common.Value.__table__
        for vn, lpk, ppk, count in (
            DBSession.query(
                cp.c.variety_name,
                vs.c.language_pk,
                vs.c.parameter_pk,
                func.count(v.c.pk),
            )
            .filter(cp.c.pk == v.c.pk)
            .filter(v.c.valueset_pk == vs.c.pk)
            .filter(vs.c.contribution_pk == prov.pk)
            .group_by(cp.c.variety_name, vs.c.language_pk, vs.c.parameter_pk)
        ):
            syns[(vn, lpk)][ppk] = count

        if syns:
            prov.synonym_index = sum(
                [sum(list(counts.values())) / len(counts) for counts in syns.values()]
            ) / len(set(syns.keys()))


#!/usr/bin/env python

"""Process all lexirumah data into a database.

Take all the data and metadata in `datasets/`, and if possible
generate a lexirumah sqlite from it.

"""

ICONS = {
    "timor-alor-pantar": "fdd0000",
    "austronesian": "c0000dd",
    "west bomberai": "f990099",
    "south bird's head": "ta0fb75",
    "east bird's head": "dff66ff",
    "konda-yahadian": "sffff00",
    "hatam-mansim": "cf38847",
    "tambora": "scccccc",
    "mor": "dcccccc",
    "mpur": "fcccccc",
    "maybrat": "ccccccc",
    "other": "o00dd00",
}


# Utility functions
def report(problem, *args, process_log=None):
    """Write a problem report to a log file.

    There is probably a `logging` module that does this better.

    """
    process_log = open(process_log, "a") if process_log else sys.stdout
    process_log.write(problem)
    for arg in args:
        process_log.write("\n  ")
        process_log.write(arg)
    process_log.write("\n")


# Define some paths.
concepticon_path = "concepts.tsv"
languages_path = "languages.tsv"
process_log = None


def import_concepticon(wordlist):
    """Load parameter (concept) data from CLDF wordlist

    Load the concepts from the pycldf word list passed as argument, and put the
    corresponding Concept objects in the database.

    """
    concepticon = {}
    for row in wordlist["ParameterTable"].iterdicts():
        id = row["ID"]
        concepticon_id = row.get("Concepticon_ID")
        if concepticon_id in ["0", "None", "???"]:
            concepticon_id = ""
        concepticon[id] = Concept(
            id=id,
            name=row["English"],
            indonesian=row["Indonesian"],
            semanticfield=row.get("Semantic_Field"),
            elicitationnotes=row["Elicitation_Notes"],
            origin=(
                "Core set"
                if identifier(row["Core_Set"] or "") == "core_set"
                else (
                    "Keraf"
                    if "Keraf" in (row["Comment"] or "")
                    or "Keraf" in (row["Core_Set"] or "")
                    else "Extended"
                )
            ),
            concepticon_id=concepticon_id,
            comment=row["Comment"] or "",
        )
    return concepticon


def create_language_object(row, families={}, identifiers={}):
    """Create a new Language object from a CLDF LanguageTable row.

    Also create its Family if necessary.

    """
    language = row["ID"]

    family = row["Family"]
    if family not in families:
        print("Creating object for language family", family)
        families[family] = Family(
            id=family.lower(), jsondata={"icon": ICONS[family.lower()]}, name=family
        )

    l = LexiRumahLanguage(
        id=row["ID"],
        name=row["Name"],
        family=families[family],
        region=row.get("Region", row.get("Macroarea")),
        latitude=row["Latitude"],
        longitude=row["Longitude"],
        description=row["Description"],
        comment=row["Comment"],
        culture=row["Culture"],
    )

    if row["Iso"]:
        iso_code = row["Iso"]
        if iso_code in identifiers:
            DBSession.add(
                LanguageIdentifier(language=l, identifier=identifiers[iso_code])
            )
        else:
            identifiers[iso_code] = iso = Identifier(
                id=iso_code, name=iso_code, type="iso639-3"
            )
            DBSession.add(LanguageIdentifier(language=l, identifier=iso))

    if language.startswith("p-"):
        glottolog_code = language.split("-")[1]
        if glottolog_code in identifiers:
            glottolog = identifiers[glottolog_code]
        else:
            glottolog = identifiers[glottolog_code] = Identifier(
                id=glottolog_code, name=glottolog_code, type="glottolog"
            )
        DBSession.add(LanguageIdentifier(language=l, identifier=glottolog))
    else:
        glottolog_code = language.split("-")
        if glottolog_code[0] in identifiers:
            glottolog = identifiers[glottolog_code[0]]
        else:
            glottolog = identifiers[glottolog_code[0]] = Identifier(
                id=glottolog_code[0], name=glottolog_code[0], type="glottolog"
            )
        DBSession.add(
            LanguageIdentifier(
                language=l,
                identifier=glottolog,
                description=("is" if len(glottolog_code) == 1 else "is dialect of"),
            )
        )

    return l


def import_languages(wordlist):
    """Load language metadata from languages tsv.

    Load the Lects from the pycldf word list passed as argument, and put the
    corresponding LexiRumahLanguage objects in the database.

    """
    lects = {}
    for row in wordlist["LanguageTable"].iterdicts():
        id = row["ID"]
        lects[id] = create_language_object(row)
    return lects


def import_sources(wordlist, contribution, contributors={}):
    """Load the bibliography"""
    contributions = {}
    by_name = {}
    for source in wordlist.sources.items():
        fields = source.entry.fields

        # Generate a citation from the source
        citation_contrib = None
        for role, people in source.entry.persons.items():
            if not people:
                continue
            names = " and ".join(map(str, people))
            fields[role] = names

            if not citation_contrib:
                if len(people) == 1:
                    citation_contrib = " ".join(people[0].last_names)
                elif len(people) == 2:
                    citation_contrib = "{:} & {:}".format(
                        " ".join(people[0].last_names), " ".join(people[1].last_names)
                    )
                else:
                    citation_contrib = "{:} et al.".format(
                        " ".join(people[0].last_names)
                    )

        if citation_contrib:
            if fields.get("year"):
                name = "{:}, {:}".format(citation_contrib, fields["year"])
            else:
                name = "{:}".format(citation_contrib)
        else:
            title_like = fields.get("title") or fields.get("note")
            if fields.get("year"):
                name = "{:}, {:}".format(title_like, fields["year"])
            else:
                name = "{:}".format(title_like)
        if name in by_name:
            name = "{:}a".format(name)
        while name in by_name:
            name = name[:-1] + chr(ord(name[-1]) + 1)

        # create a contribution
        contrib = LexiRumahSource(
            id=source.id,
            name=name,
            bibtex_type=vars(EntryType).get(source.genre) or EntryType.misc,
            provider=contribution,
        )
        for key, value in fields.items():
            if hasattr(contrib, key) and not getattr(contrib, key):
                setattr(contrib, key, value)
            else:
                contrib.jsondata[key] = value

        DBSession.add(contrib)
        contributions[source.id] = contrib
        by_name[name] = contrib

    return contributions


def import_forms(
    wordlist,
    concepticon,
    languages,
    bibliography,
    contribution,
    trust=[],
    valuesets={},
    values={},
    cognatesets={},
    COGNATESETS_CONTRIB=None,
):
    """Load a word list from a file.

    Import a contribution (tsv dataset and its metadata file)
    corresponding to one word list (may contain several languages)
    from `path`.

    `trust` is a list of filenames we have to assume to be correct,
    and are not permitted to write back to.  All other files may be
    updated.

    """

    # Import all the rows.
    loans = {}
    for loan in wordlist["BorrowingTable"].iterdicts():
        if loan["Status"] > loans.get("Form_ID_Target", 0):
            loans[loan["Form_ID_Target"]] = loan
    forms = {}
    for row in wordlist["FormTable"].iterdicts():
        language = row["Lect_ID"]
        feature = row["Concept_ID"]
        sources = [bibliography[s] for s in row["Source"]]

        # Create the objects representing the form in the
        # database. This is a value in a value set.
        value = row["Form"]

        vsid = identifier("{:s}-{:}".format(language, feature))
        try:
            vs = valuesets[vsid]
        except KeyError:
            vs = valuesets[vsid] = ValueSet(
                vsid,
                parameter=concepticon[feature],
                language=languages[language],
                contribution=contribution,
            )
        vid = row["ID"]
        form = Counterpart(
            id=vid,
            valueset=vs,
            orthographic_form=row["Local_Orthography"],
            loan=loans.get(row["ID"], {"Status": 0})["Status"],
            comment=row["Comment"],
            name=value,
            segments=" ".join([c or "" for c in row["Segments"]]),
        )
        for source in sources:
            DBSession.add(
                CounterpartReference(
                    counterpart=form,
                    form_given_as=row["Form_according_to_Source"],
                    source=source,
                )
            )
        forms[vid] = form
        DBSession.add(form)
    return forms


def import_cognatesets(dataset, forms, bibliography, contribution, cognatesets={}):
    cognateset_by_formid = {}
    cognateset_forms = {}

    for row in dataset["CognateTable"].iterdicts():
        # Only incorporate the newest cognate codings, and be robust about that
        try:
            cs = cognateset_forms.setdefault(row["Cognateset_ID"], [])
            cs.append(forms[row["Form_ID"]].name)
            row["CognateForms"] = cs
            cognateset_by_formid[row["Form_ID"]] = row
        except KeyError:
            continue
    for row in cognateset_by_formid.values():
        cognateset_id = row["Cognateset_ID"]
        try:
            cognateset = cognatesets[cognateset_id]
        except KeyError:
            row["CognateForms"].sort()
            cognateset = cognatesets[cognateset_id] = Cognateset(
                id=row["Cognateset_ID"],
                contribution=contribution,
                name=row["CognateForms"][len(row["CognateForms"]) // 2],
            )
        assoc = CognatesetCounterpart(
            cognateset=cognateset,
            doubt=True if "LexStat" in row["Source"] else False,
            alignment=(None if not row["Alignment"] else " ".join(row["Alignment"])),
            counterpart=forms[row["Form_ID"]],
        )
        for source in row["Source"]:
            DBSession.add(
                CognatesetCounterpartReference(
                    cognatesetcounterpart_pk=assoc.pk, source=bibliography[source]
                )
            )


def db_main():
    """Build the database.

    Load the CLDF dataset and turn it into a SQLite dataset.
    """
    dataset = get_dataset()

    g = dataset.properties.get

    ds = Dataset(
        id=g("dc:identifier", identifier(g("dc:title", "Wordlist"))),
        name=g("dc:title", g("dc:identifier", "Wordlist").title()),
        publisher_name=g("dc:publisher", None),
        # publisher_place=dataset_metadata["publisher_place"],
        # publisher_url=dataset_metadata["publisher_url"],
        license=g("dc:license", None),
        domain=g("clld:domain", "localhost"),
        contact=g("clld:contact"),
        jsondata={
            "license_icon": "cc-by.png",
            "license_name": "Creative Commons Attribution 4.0 International License",
        },
    )
    DBSession.add(ds)

    provider = Provider(
        id=ds.id,
        name=ds.name,
        description=g("dc:description"),
        license=g("dc:license"),
        jsondata={},
        url="",
    )

    contributors = {}
    # FIXME: Don't use ID hack, instead hand contributors dict
    # through.
    for i, editor in enumerate(g("dc:creator", [])):
        contributor_id = identifier(editor)
        try:
            contributor = contributors[contributor_id]
        except KeyError:
            contributors[contributor_id] = contributor = Contributor(
                id=contributor_id, name=editor
            )
        DBSession.add(Editor(dataset=ds, contributor=contributor, ord=i, primary=True))
    for i, editor in enumerate(g("dc:contributor", [])):
        contributor_id = identifier(editor)
        try:
            contributor = contributors[contributor_id]
        except KeyError:
            contributors[contributor_id] = contributor = Contributor(
                id=contributor_id, name=editor
            )
        DBSession.add(
            Editor(
                dataset=ds,
                contributor=contributor,
                ord=i + len(g("dc:creator", [])),
                primary=False,
            )
        )

    concepticon = import_concepticon(dataset)
    languages = import_languages(dataset)
    sources = import_sources(dataset, contribution=provider)
    forms = import_forms(
        dataset, concepticon, languages, sources, contribution=provider
    )
    cognatesets = import_cognatesets(dataset, forms, sources, contribution=provider)


def main():
    """Construct a new database from scratch."""
    print(os.path.join(os.path.dirname(__file__), "lexirumah_for_create_database.ini"))
    args = parsed_args(
        args=[
            os.path.join(os.path.dirname(__file__), "lexirumah_for_create_database.ini")
        ]
    )

    with transaction.manager:
        db_main()
    with transaction.manager:
        init_main(args)


if __name__ == "__main__":
    main()
