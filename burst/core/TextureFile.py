__all__ = ['TextureFile']


import pathlib

from typing import Union

from panda3d import core as p3d


class TextureFile(burst.control.File,
                  extensions = ['.jpg', '.png', '.gif']):

    def read(self, *,
             alpha: Union[str, pathlib.Path, p3d.Filename,
                          burst.control.File] = None,
             ) -> p3d.Texture:
        """
        Attempts to load the TexFile as a Texture. An alpha File/path may be
        additionally supplied.
        """
        if alpha is not None:
            if isinstance(alpha, p3d.Filename):
                alpha = alpha.to_os_specific()

            if isinstance(alpha, burst.control.File):
                alpha = alpha.get_path()

        if (alpha is None) or isinstance(alpha, (str, pathlib.Path)):
            return base.loader.load_texture(self.get_path(), alpha)
        else:
            raise TypeError(f'invalid alpha: {alpha!r}')
