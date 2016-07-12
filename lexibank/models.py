from uuid import uuid1

from zope.interface import implementer
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import (
    Language, Parameter, Contribution, Value, HasSourceMixin, Source,
)

from clld_glottologfamily_plugin.models import HasFamilyMixin

from lexibank.interfaces import ICognateset


def uuid():
    return uuid1().urn.split(':')[2]


@implementer(interfaces.IContribution)
class Provider(CustomModelMixin, Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    language_count = Column(Integer)
    parameter_count = Column(Integer)
    lexeme_count = Column(Integer)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    representation = Column(Integer)
    semanticfield = Column(Unicode)

    @property
    def concepticon_url(self):
        return 'http://concepticon.clld.org/parameters/{0}'.format(self.id)


@implementer(interfaces.ILanguage)
class LexibankLanguage(CustomModelMixin, Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)


@implementer(interfaces.ISource)
class LexibankSource(CustomModelMixin, Source):
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)
    provider_pk = Column(Integer, ForeignKey('provider.pk'))
    provider = relationship(Provider, backref='sources')


@implementer(ICognateset)
class Cognateset(Base):
    id = Column(String, default=uuid, unique=True)
    name = Column(Unicode, unique=True)
    # FIXME: are cognate sets concept-specific? If so, they should be related to the
    # corresponding Concept.


@implementer(interfaces.IValue)
class Counterpart(CustomModelMixin, Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    cognateset_pk = Column(Integer, ForeignKey('cognateset.pk'))
    cognateset = relationship(Cognateset, backref='counterparts')
    loan = Column(Boolean, default=False)


class CounterpartReference(Base, HasSourceMixin):
    counterpart_pk = Column(Integer, ForeignKey('counterpart.pk'))
    counterpart = relationship(Counterpart, backref="references")
