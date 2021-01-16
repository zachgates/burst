#!/usr/local/bin/python3.9

import pathlib
import re

from typing import Optional, Union

from panda3d import core as p3d


EXTENSION_EXPR = '^\.(\w+)$'


def validate_extensions(*extensions: str,
                        pattern: Union[str, re.Pattern] = EXTENSION_EXPR,
                        match_group: int = 1,
                        ) -> set:
    """
    Compares each extensions with the pattern expression to validate it as
    a filetype. A pattern and/or match group may be additionally specified.
    """
    if not isinstance(pattern, (str, re.Pattern)):
        raise ValueError('expected string or re.Pattern for pattern')

    if not isinstance(match_group, int):
        raise ValueError('expected integer for match_group')

    fexts = set()

    for fext in extensions:
        if isinstance(fext, str):
            if match := re.fullmatch(pattern, fext):
                fexts.add(match.group(match_group))
            else:
                raise ValueError(f'invalid extension: {fext!r}')
        else:
            raise TypeError(f'invalid extension: {fext!r}')

    return fexts


class ExtensionsMixin(object):
    """
    A mixin class for defining a set of extensions on the object upon
    initialization.
    """

    def __init__(self, extensions: Union[list, tuple, set]):
        super().__init__()
        self.__extensions = tuple(validate_extensions(*extensions))

    def get_extensions(self) -> tuple:
        return self.__extensions

    getExtensions = get_extensions
    extensions = property(get_extensions)


class _File(type, ExtensionsMixin):

    def __new__(cls, name, bases, dct, **kwargs):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, /, *,
                 extensions: Union[list, tuple, set] = (),
                 ) -> type:
        type.__init__(cls, name, bases, dct)
        ExtensionsMixin.__init__(cls, extensions)


class File(object, metaclass = _File):

    def __new__(cls, vfile: p3d.VirtualFile):
        for typ in cls.__subclasses__():
            if vfile.get_filename().get_extension() in typ.extensions:
                return typ(vfile)
        else:
            return super().__new__(cls)

    def __init__(self, vfile: p3d.VirtualFile):
        if isinstance(vfile, p3d.VirtualFile):
            super().__init__()
            self.__vfile = vfile
        else:
            raise ValueError('expected panda3d.core.VirtualFile for vfile')

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self.path.name)

    def get_path(self) -> pathlib.Path:
        return pathlib.Path(self.__vfile.get_filename().to_os_specific())

    getPath = get_path
    path = property(get_path)


class TexFile(File, extensions = ['.jpg', '.png', '.gif']):

    def load(self, /, *, alpha_file: Optional[File] = None) -> p3d.Texture:
        """
        Attempts to load the TexFile as a Texture. An alpha file may be
        additionally supplied.
        """
        if (alpha_file is not None) and not isinstance(alpha_file, File):
            raise TypeError('expected src.core.File for alpha_file')
        else:
            return base.loader.load_texture(
                self.path,
                alpha_file.path if alpha_file else None,
                )
