
import sys
import os
import transaction
import pandas

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld_glottologfamily_plugin.util import load_families

import lexibank
from lexibank.scripts.util import import_cldf
from lexibank.models import LexibankLanguage, Concept


# Only while testing
import random

def main(args):
    datadir = "j:/ResearchData/HUM/LUCL-KlamerVICI/sunda_database/"
    LEXIBANK_REPOS = os.path.join(datadir, "lexibank")
    
    with transaction.manager:
        dataset = common.Dataset(
            id=lexibank.__name__+str(random.randint(0,200000)),
            name="LexiSunDa",
            publisher_name="Leiden University Centre for Linguistics",
            publisher_place="Leiden",
            publisher_url="http://www.universiteitleiden.nl/en/humanities/leiden-university-centre-for-linguistics",
            license="http://creativecommons.org/licenses/by/4.0/",
            domain="lexisunda.leiden.edu",
            contact="g.a.kaiping@hum.leidenuniv.nl",
            jsondata={
                'license_icon': "cc-by.png",
                'license_name': "Creative Commons Attribution 4.0 International License"})
        DBSession.add(dataset)

    concepts = pandas.io.parsers.read_csv(os.path.join(LEXIBANK_REPOS, "concepts.tsv"),
                                          index_col="Concept ID", sep="\t", encoding="utf-16")
    languages = pandas.io.parsers.read_csv(os.path.join(datadir, "languages.tsv"),
                                           index_col="Language ID", encoding="utf-16", sep="\t")
    print(languages)
    import_cldf(os.path.join(LEXIBANK_REPOS, "datasets"), concepts, languages)

    with transaction.manager:
        load_families(Data(),
                      #FIXME: THROW AN ERROR INSTEAD OF ASSUMING IT'S AUSTRONESIAN
                      [(("aust1307" if pandas.isnull(language.glottolog) else language.glottolog),
                        language)
                       for language in DBSession.query(LexibankLanguage)
                       if language],
                      isolates_icon='tcccccc')


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    for concept in DBSession.query(Concept):
        concept.representation = DBSession.query(common.ValueSet)\
            .filter(common.ValueSet.parameter_pk == concept.pk)\
            .count()


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
