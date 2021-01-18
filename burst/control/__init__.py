__all__ = [
    'validate_extensions', 'ExtensionsMixin', 'File', 'TextureFile',
    'FileManager', 'ObjectManager', 'SelectionManager',
]


import contextlib
import pathlib
import re

from typing import Iterable

from panda3d import core as p3d

from direct.stdpy.file import StreamIOWrapper


_EXTENSION_EXPR = re.compile('^\.(\w+)$')


def validate_extensions(*extensions: str,
                        pattern: re.Pattern = _EXTENSION_EXPR,
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
            match = pattern.fullmatch(ext)
            if match:
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

    def get_extensions(self) -> tuple:
        return self.__extensions

    extensions = property(get_extensions)


class _File(type, ExtensionsMixin):

    def __new__(cls, name, bases, dct, **kwargs):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, *,
                 extensions: Iterable[str] = (),
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
        self.__filename = path

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.path.name)

    def get_filename(self):
        return p3d.Filename(self.__filename)

    def get_path(self) -> pathlib.Path:
        return pathlib.Path(self.__filename.to_os_specific())

    path = property(get_path)


from .FileManager import FileManager
from .ObjectManager import ObjectManager
from .SelectionManager import SelectionManager
