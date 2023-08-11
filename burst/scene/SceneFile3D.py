__all__ = [
    'JSONFile',
    'SceneFile3D',
]


import burst
import json

import panda3d.core as p3d

from direct.stdpy.file import open

from burst.control import File


class JSONFile(File, extensions = ['.json']):

    def read(self) -> dict:
        with open(self.path) as file:
            return json.load(file)


class SceneFile3D(File, extensions = ['.burst3d']):

    # TODO: bake the assets (models, textures, layout) into the file itself

    def read(self) -> dict:
        # TODO: replace the following once the JSON layout is baked
        path = self.path.with_suffix('.json')
        data = burst.store.load_file(path).read()
        ... # TODO: pipeline the JSON data into dataclasses
        return data
