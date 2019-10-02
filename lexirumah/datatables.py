# coding: utf-8
from __future__ import unicode_literals

from sqlalchemy.orm import joinedload, joinedload_all

from clld.db.meta import DBSession
from clld.db.util import get_distinct_values
from clld.db.models.common import Value, Contribution, ValueSet, Parameter, Language, Source
from clld.web.util.helpers import external_link, linked_references, link

from clld.web.datatables.base import Col, IdCol, LinkCol, LinkToMapCol, DataTable
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values
from clld.web.datatables.contribution import Contributions
from clld.web.datatables.source import Sources

from clld_glottologfamily_plugin.datatables import MacroareaCol, FamilyCol as FamilyLinkCol
from clld_glottologfamily_plugin.models import Family

from .models import (
    LexiRumahLanguage, Counterpart, Concept, Provider, LexiRumahSource,
    CounterpartReference, Cognateset,
)


class ProviderCol(LinkCol):
    def __init__(self, dt, name='reference', **kw):
        kw.setdefault('model_col', Provider.name)
        kw.setdefault('get_object', lambda i: i.provider)
        kw['choices'] = [(p.id, p.name) for p in DBSession.query(Provider)]
        LinkCol.__init__(self, dt, name, **kw)

    def search(self, qs):
        return Contribution.id == qs


class SourcesCol(LinkCol):
    def format(self, item):
        links = []
        for it in self.get_obj(item):
            try:
                links.append(
                    link(self.dt.req, it, **self.get_attrs(it)))
            except AssertionError:
                links.append(it)
        return '; '.join(links)


from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.datatables.source import TypeCol
class LexiRumahSources(Sources):
    def base_query(self, query):
        query = Sources.base_query(self, query)
        query = query.join(LexiRumahSource.provider).options(joinedload(LexiRumahSource.provider))
        return query

    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
            Col(self, 'author'),
            Col(self, 'year'),
            Col(self, 'title'),
            TypeCol(self, 'bibtex_type'),
        ]

def get_counterpart_references(counterpart):
    for i in counterpart.references:
        yield i.source


class ItalicsCol(Col):
    def format_value(self, value):
        return "<i>{:}</i>".format(super().format_value(value))


class Counterparts(Values):
    __constraints__ = [Parameter, Contribution, Language, Source]

    def base_query(self, query):
        query = query.join(ValueSet).options(
            joinedload(Value.valueset),
            joinedload_all(Counterpart.references, CounterpartReference.source)
        )

        if self.language:
            query = query \
                .join(ValueSet.parameter) \
                .join(ValueSet.contribution) \
                .options(
                    joinedload(Value.valueset, ValueSet.contribution),
                    joinedload(Value.valueset, ValueSet.parameter))
            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            query = query \
                .join(ValueSet.language) \
                .outerjoin(LexiRumahLanguage.family) \
                .options(joinedload_all(
                    Value.valueset, ValueSet.language, LexiRumahLanguage.family))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        if self.source:
            query = query.filter(self.source.pk == CounterpartReference.source_pk)
            query = query.filter(CounterpartReference.counterpart_pk == Value.pk)
            return query

        return query \
            .join(ValueSet.parameter)\
            .join(ValueSet.language)\
            .options(
                joinedload(Value.valueset, ValueSet.parameter),
                joinedload(Value.valueset, ValueSet.language),
            )

    def col_defs(self):
        template = [
            FamilyLinkCol(self, 'family', LexiRumahLanguage, get_object=lambda i: i.valueset.language),
            LinkCol(
                self,
                'lect',
                model_col=LexiRumahLanguage.name,
                get_object=lambda i: i.valueset.language),
            LinkCol(
                self,
                'concept',
                model_col=Concept.name,
                get_object=lambda i: i.valueset.parameter),
            LinkCol(
                self,
                'Form (IPA)',
                sTitle='Form (IPA)',
                model_col=Counterpart.name),
            ItalicsCol(
                self,
                'orthography',
                model_col=Counterpart.orthographic_form),
            # Col(self, 'loan', model_col=Counterpart.loan),
            Col(self, 'comment', model_col=Counterpart.comment),
            SourcesCol(
                self,
                'sources',
                model_col=LexiRumahSource.name,
                get_object=get_counterpart_references),
            Col(
                self,
                'given as',
                model_col=CounterpartReference.form_given_as,
                get_object=lambda i: i.references[0] if i.references else None),
        ]
        if self.source:
            del template[6]
        if self.parameter:
            del template[2]
        if self.language:
            del template[1]
            del template[0]
        return template


#class FeatureIdCol(IdCol):
#    def search(self, qs):
#        if self.model_col:
#            return self.model_col.contains(qs)

#    def order(self):
#        return Feature.sortkey_str, Feature.sortkey_int


class LanguageIdCol(LinkCol):
    def get_attrs(self, item):
        return dict(label=item.id)


class GlottologLinkCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        if item.glottolog_url:
            return external_link(item.glottolog_url, label=item.glottocode)
        else:
            return ''


class EthnologueLinkCol(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        if item.ethnologue_url:
            return external_link(item.ethnologue_url, label=item.iso_code)
        else:
            return ''


class LexiRumahLanguages(Languages):
    __constraints__ = [Contribution]

    def base_query(self, query):
        if self.contribution:
            sq = DBSession.query(ValueSet.language_pk)\
                .filter(ValueSet.contribution_pk == self.contribution.pk)\
                .distinct()\
                .subquery()
            query = query.filter(LexiRumahLanguage.pk.in_(sq))
        return query.outerjoin(Family).options(joinedload(LexiRumahLanguage.family))

    def col_defs(self):
        return [
            LanguageIdCol(self, 'id'),
            LinkCol(self, 'name'),
            LinkToMapCol(self, 'm'),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
            Col(self, 'region', model_col=LexiRumahLanguage.region),
            FamilyLinkCol(self, 'family', LexiRumahLanguage),
            GlottologLinkCol(self, 'Glottolog'),
            EthnologueLinkCol(self, 'Ethnologue'),
        ]


class ConcepticonLink(Col):
    __kw__ = {'bSearchable': False, 'bSortable': False}

    def format(self, item):
        if item.concepticon_url:
            return external_link(item.concepticon_url)
        else:
            return ''


class Concepts(Parameters):
    def col_defs(self):
        return [
            LinkCol(self, 'name', sTitle='Concept'),
            Col(self, 'indonesian',
                model_col=Concept.indonesian,
                bSearchable=True),
            Col(self, '# lects', model_col=Concept.representation,
                bSearchable=False,
                sDescription='<small>The number of languages where this concept is given</small>'),
            Col(self, 'semantic_field', model_col=Concept.semanticfield, choices=get_distinct_values(Concept.semanticfield)),
            ConcepticonLink(self, 'Concepticon'),
        ]


class Providers(Contributions):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            LinkCol(self, 'reference'),
            #Col(self, 'description', model_col=Contribution.description),
            Col(self, 'language_count', sTitle='# lects', model_col=Provider.language_count),
            Col(self, 'parameter_count', sTitle='# concepts', model_col=Provider.parameter_count),
            Col(self,
                'lexeme_count',
                sTitle='# lexemes',
                model_col=Provider.lexeme_count,
                format=lambda i: '{:,}'.format(i.lexeme_count)),
            Col(self,
                'synonymy',
                sDescription=Provider.synonym_index.doc,
                model_col=Provider.synonym_index,
                format=lambda i: '{:.3f}'.format(i.synonym_index))
        ]


def get_cognateset_references(cognateset):
    for i in cognateset.references:
        yield i.source

class Cognatesets(DataTable):
    def base_query(self, query):
        return query.join(Contribution)

    def col_defs(self):
        result = [
#             IdCol(self, 'id'),
            LinkCol(self, 'name'),
            Col(self, 'cognates', model_col=Cognateset.representation),
#             ProviderCol(
#                 self,
#                 'reference',
#                 get_object=lambda i: str(vars(i))),
        ]
        return result
        


def includeme(config):
    config.register_datatable('cognatesets', Cognatesets)
    config.register_datatable('languages', LexiRumahLanguages)
    config.register_datatable('contributions', Providers)
    config.register_datatable('parameters', Concepts)
    config.register_datatable('values', Counterparts)
    config.register_datatable('sources', LexiRumahSources)
