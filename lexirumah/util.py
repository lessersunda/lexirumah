# coding: utf8
from __future__ import unicode_literals, division
from itertools import groupby

from sqlalchemy import func, desc, text
from sqlalchemy.orm import joinedload, joinedload_all
from clld_glottologfamily_plugin.models import Family
from clld import RESOURCES
from clld.db.meta import DBSession
from clld.db.models.common import Language, Value, ValueSet
from clld.web.util.htmllib import HTML
from clld.web.maps import SelectedLanguagesMap

from lexirumah.models import LexiRumahLanguage, Source, Counterpart
from lexirumah.maps import HighZoomSelectedLanguagesMap


def concepticon_link(request, concept):
    return HTML.a(
        HTML.img(
            src=request.static_url('lexirumah:static/concepticon_logo.png'),
            height=20,
            width=30),
        title='corresponding concept set at Concepticon',
        href=concept.concepticon_url)


def value_detail_html(context=None, request=None, **kw):
    syns = DBSession.query(Value)\
                    .join(ValueSet)\
                    .filter(Value.pk != context.pk)\
                    .filter(ValueSet.parameter_pk == context.valueset.parameter_pk)\
                    .filter(ValueSet.language_pk == context.valueset.language_pk)

    colexifications = DBSession.query(Value)\
                      .join(Counterpart)\
                      .join(ValueSet)\
                      .filter(Counterpart.pk != context.pk)\
                      .filter(Counterpart.segments == context.segments)\
                      .filter(ValueSet.language_pk == context.valueset.language_pk)

    return {'synonyms': list(syns),
            'colexifications': list(colexifications),
    }


def contribution_detail_html(context=None, request=None, **kw):
    langs = DBSession.query(Language)\
        .filter(Language.pk.in_(context.jsondata['language_pks']))\
        .options(joinedload(LexiRumahLanguage.family))
    return {'map': HighZoomSelectedLanguagesMap(context, request, list(langs))}


def dataset_detail_html(context=None, request=None, **kw):
    families = DBSession.query(Family.id, Family.name, func.count(LexiRumahLanguage.id).label('c'))\
        .join(LexiRumahLanguage)\
        .group_by(Family.id, Family.name)\
        .order_by(desc(text('c')))
    example_reference = DBSession.query(Source).first()

    return dict(
        families=families,
        example_reference=example_reference,
        stats=context.get_stats([rsc for rsc in RESOURCES if rsc.name in [
            'language', 'family', 'cognateset', 'source', 'value', 'parameter']]))


