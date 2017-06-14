from clld.web.maps import Map, ParameterMap, LanguageMap, SelectedLanguagesMap
from clld.web.adapters.geojson import get_lonlat


class HighZoomParameterMap (ParameterMap):
    def get_options(self):
        return {'info_query': {'parameter': self.ctx.pk}, 'hash': True,
                'max_zoom': 11, 'icon_size': 20}

class HighZoomLanguageMap (LanguageMap):
    def get_options(self):
        return {
            'center': list(reversed(get_lonlat(self.ctx) or [0, 0])),
            'zoom': 9,
            'no_popup': True,
            'no_link': True,
            'sidebar': True,
            'max_zoom': 11,
            'icon_size': 20}
    
class HighZoomMap (Map):
    def get_options(self):
        return {'max_zoom': 11, 'icon_size': 20}


class HighZoomSelectedLanguagesMap (SelectedLanguagesMap):
    def get_options(self):
        options = SelectedLanguagesMap.get_options(self)
        options.update({'max_zoom': 11, 'icon_size': 20})
        return options

    
def includeme(config):
    config.register_map('parameter', HighZoomParameterMap)
    config.register_map('language', HighZoomLanguageMap)
    config.register_map('languages', HighZoomMap)
