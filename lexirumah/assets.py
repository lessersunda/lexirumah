from pathlib import Path

from clld.web.assets import environment

import lexirumah


environment.append_path(
    str(Path(lexirumah.__file__).parent.joinpath('static')), url='/lexirumah:static/')
environment.load_path = list(reversed(environment.load_path))
