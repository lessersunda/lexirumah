from clld.web.maps import ParameterMap, Map


class ConceptMap(ParameterMap):
    def get_options(self):
        return {"icon_size": 15, "max_zoom": 13}


class LanguagesMap(Map):
    def get_options(self):
        return {"icon_size": 15, "max_zoom": 13}


def includeme(config):
    config.register_map("parameter", ConceptMap)
    config.register_map("languages", LanguagesMap)
