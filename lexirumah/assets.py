from clld.web.assets import environment
from clldutils.path import Path

import lexirumah


environment.append_path(
    Path(lexirumah.__file__).parent.joinpath('static').as_posix(), url='/lexirumah:static/')
environment.load_path = list(reversed(environment.load_path))
