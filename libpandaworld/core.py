#!/usr/local/bin/python3.9

import pathlib
import re

from typing import Iterable, Union

from panda3d import core as p3d


EXTENSION_EXPR = re.compile('^\.(\w+)$')


def validate_extensions(*extensions: str,
                        pattern: re.Pattern = EXTENSION_EXPR,
                        match_group: int = 1,
                        ) -> set:
    """
    Compares each extensions with the pattern expression to validate it as
    a filetype. A pattern and/or match group may be additionally specified.
    """
    if not isinstance(pattern, re.Pattern):
        raise ValueError('expected re.Pattern for pattern')

    if not isinstance(match_group, int):
        raise ValueError('expected integer for match_group')

    exts = set()
    for ext in extensions:
        if isinstance(ext, str):
            if match := pattern.fullmatch(ext):
                exts.add(match.group(match_group))
            else:
                raise ValueError(f'invalid extension: {ext!r}')
        else:
            raise TypeError(f'invalid extension: {ext!r}')

    return exts


class ExtensionsMixin(object):
    """
    A mixin class for defining a set of extensions on the object upon
    initialization.
    """

    def __init__(self, *extensions: str):
        super().__init__()
        self.__extensions = tuple(validate_extensions(*extensions))

    def GET_EXTENSIONS(self) -> tuple:
        return self.__extensions

    extensions = property(GET_EXTENSIONS)


class _File(type, ExtensionsMixin):

    def __new__(cls, name, bases, dct, **kwargs):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, /, *,
                 extensions: Iterable = (),
                 ) -> type:
        type.__init__(cls, name, bases, dct)
        ExtensionsMixin.__init__(cls, *extensions)


class File(object, metaclass = _File):

    def __new__(cls, path: p3d.Filename):
        if not isinstance(path, p3d.Filename):
            raise ValueError('expected panda3d.core.Filename for path')

        for typ in cls.__subclasses__():
            if path.get_extension() in typ.extensions:
                return typ(path)
        else:
            return super().__new__(cls)

    def __init__(self, path: p3d.Filename):
        super().__init__()
        self.__path = path

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.path.name)

    def GET_PATH(self) -> pathlib.Path:
        return pathlib.Path(self.__path.to_os_specific())

    path = property(GET_PATH)


class TextureFile(File, extensions = ['.jpg', '.png', '.gif']):

    def read(self, /, *,
             alpha: Union[str, pathlib.Path, p3d.Filename, File] = None,
             ) -> p3d.Texture:
        """
        Attempts to load the TexFile as a Texture. An alpha File/path may be
        additionally supplied.
        """
        if alpha is not None:
            if isinstance(alpha, p3d.Filename):
                alpha = alpha.to_os_specific()
            if isinstance(alpha, File):
                alpha = alpha.get_path()

        if (alpha is None) or isinstance(alpha, (str, pathlib.Path)):
            return base.loader.load_texture(self.get_path(), alpha)
        else:
            raise TypeError(f'invalid alpha: {alpha!r}')
