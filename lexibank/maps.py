from clld.web.maps import Map, ParameterMap, LanguageMap

class HighZoomParameterMap (ParameterMap):
    def get_options(self):
        return {'max_zoom': 10, 'icon_size': 20}

class HighZoomLanguageMap (LanguageMap):
    def get_options(self):
        return {'max_zoom': 10, 'icon_size': 20}
    
class HighZoomMap (Map):
    def get_options(self):
        return {'max_zoom': 10, 'icon_size': 20}
    
def includeme(config):
    config.register_map('parameter', HighZoomParameterMap)
    config.register_map('language', HighZoomLanguageMap)
    config.register_map('languages', HighZoomMap)
