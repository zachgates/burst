__all__ = [
    'ModelFile',
    'TextureFile',
]


import json
import pathlib
import typing

import panda3d.core as p3d

from direct.stdpy.file import open

from burst.control import File


class ModelFile(File, extensions = ['.bam', '.egg']):

    def read(self):
        return base.loader.load_model(self.path)


class TextureFile(File, extensions = ['.jpg', '.png', '.gif']):

    def read(self, /, *,
             alpha: typing.Union[bool,
                                 str, pathlib.Path, p3d.Filename,
                                 File,
                                 ] = False,
             ) -> p3d.Texture:
        """
        Attempts to load the TexFile as a Texture. An alpha File/path may be
        additionally supplied.
        """
        if alpha is True:
            if not (alpha := self.path.with_suffix('.rgb')).exists():
                alpha = False

        if alpha is False:
            return base.loader.load_texture(self.path)

        if isinstance(alpha, p3d.Filename):
            alpha = alpha.to_os_specific()

        if isinstance(alpha, File):
            alpha = alpha.get_path()

        if isinstance(alpha, (str, pathlib.Path)):
            return base.loader.load_texture(self.path, alpha)
        else:
            raise TypeError(f'invalid alpha: {alpha!r}')


class JSONFile(File, extensions = ['.json']):

    def read(self) -> dict:
        with open(self.path) as fp:
            return json.load(fp)
