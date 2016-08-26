from __future__ import unicode_literals

from clld.web.maps import Map, ParameterMap, LanguageMap


class ConceptMap(ParameterMap):
    def get_options(self):
        return {'max_zoom': 12, 'icon_size': 15}


class LanguagesMap(Map):
    def get_options(self):
        return {'max_zoom': 12, 'icon_size': 20}


class ZoomLanguageMap(LanguageMap):
    def get_options(self):
        return {'max_zoom': 12, 'icon_size': 20}


def includeme(config):
    config.register_map('parameter', ConceptMap)
    config.register_map('language', ZoomLanguageMap)
    config.register_map('languages', LanguagesMap)
