__all__ = ['TextureFile']


import pathlib

from typing import Union

import panda3d.core as p3d


class TextureFile(burst.control.File, extensions = ['.jpg', '.png', '.gif']):

    def read(self, /, *,
             alpha: Union[bool, str, pathlib.Path, p3d.Filename,
                          burst.control.File] = None,
             ) -> p3d.Texture:
        """
        Attempts to load the TexFile as a Texture. An alpha File/path may be
        additionally supplied.
        """
        if alpha is True:
            if not (alpha := self.path.with_suffix('.rgb')).exists():
                alpha = None

        if alpha is None:
            return base.loader.load_texture(self.path)

        if isinstance(alpha, p3d.Filename):
            alpha = alpha.to_os_specific()

        if isinstance(alpha, burst.control.File):
            alpha = alpha.get_path()

        if isinstance(alpha, (str, pathlib.Path)):
            return base.loader.load_texture(self.path, alpha)
        else:
            raise TypeError(f'invalid alpha: {alpha!r}')
