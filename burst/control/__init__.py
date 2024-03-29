__all__ = [
    'validate_extensions',
    'ExtensionsMixin',
    'File',
    'FileManager',
    'SelectionManager',
    'ObjectManager',
]


import abc
import contextlib
import pathlib
import re
import typing

import panda3d.core as p3d


_EXTENSION_EXPR = re.compile('^\.(\w+)$')


def validate_extensions(extensions: typing.Iterable[str],
                        pattern: re.Pattern = _EXTENSION_EXPR,
                        match_group: int = 1,
                        ) -> set:
    """
    Compares each extension with the pattern expression to validate it as
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

    def __init__(self, extensions: typing.Iterable[str]):
        super().__init__()
        self.__extensions = tuple(validate_extensions(extensions))

    def get_extensions(self) -> tuple:
        return self.__extensions

    extensions = property(get_extensions)


class _File(abc.ABCMeta, ExtensionsMixin):

    def __new__(cls, name, bases, dct, **kwargs):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, /, *,
                 extensions: typing.Iterable[str] = (),
                 ) -> type:
        abc.ABCMeta.__init__(cls, name, bases, dct)
        ExtensionsMixin.__init__(cls, extensions)


class File(object, metaclass = _File):

    def __new__(cls, path: p3d.Filename):
        if not isinstance(path, p3d.Filename):
            raise ValueError('expected panda3d.core.Filename for path')

        for type_ in cls.__subclasses__():
            if path.get_extension() in type_.extensions:
                return type_(path)
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

    @abc.abstractmethod
    def read(self) -> typing.Any:
        raise NotImplementedError()


from .FileManager import *
from .SelectionManager import *
from .ObjectManager import *
