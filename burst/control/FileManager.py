__all__ = [
    'VFS',
    'FileManager',
]


import pathlib
import re
import sys
import typing

import panda3d.core as p3d

from direct.showbase.DirectObject import DirectObject

from burst.control import validate_extensions, ExtensionsMixin, File


VFS = p3d.VirtualFileSystem.get_global_ptr()


def normalize_path(path: typing.Union[str, pathlib.Path, p3d.Filename]):
    if isinstance(path, (str, pathlib.Path)):
        path = p3d.Filename.from_os_specific(str(path))

    if isinstance(path, p3d.Filename):
        return path
    else:
        raise TypeError('expected string, pathlib.Path, '
                        'or panda3d.core.Filename for path')


class FileManager(DirectObject, ExtensionsMixin):

    def __init__(self,
                 search_path: p3d.DSearchPath,
                 # extensions: list[str] = [],
                 ):

        DirectObject.__init__(self)
        # ExtensionsMixin.__init__(self, extensions)

        if isinstance(search_path, p3d.DSearchPath):
            self.search_path = search_path
        else:
            raise TypeError('expected panda3d.core.DSearchPath for path')

    def add_search_path(self,
                        path: typing.Union[str, pathlib.Path, p3d.Filename],
                        ):
        self.search_path.append_directory(normalize_path(path))

    def scan_path(self,
                  path: typing.Union[str, pathlib.Path, p3d.Filename],
                  ) -> p3d.Filename:
        """
        Attempts to find the given path, creating a VirtualFile pointer.
        """
        if VFS.resolve_filename(path := normalize_path(path),
                                self.search_path,
                                ):
            return path
        else:
            raise FileNotFoundError(path)

    def load_file(self, path: p3d.Filename) -> File:
        """
        Attempts to create a File object from its VirtualFile pointer.
        """
        path = self.scan_path(path)

        # if (path.get_extension() in self.extensions) or not self.extensions:
        return File(path)
        # else:
        #     raise ValueError(f'cannot load filetype: {path.get_extension()}')

    def load_directory(self, path, /, *,
                       recursive: bool = False,
                       extensions: typing.Iterable[str] = (),
                       ) -> list[File]:
        """
        Attempts to find and load a directory of Files from the given path.
        A recursive loading flag may also be supplied, and/or a group of
        extensions to use as a filter.
        """
        if isinstance(extensions, typing.Container):
            extensions = validate_extensions(extensions)

        if not (path := self.scan_path(path)).is_directory():
            raise NotADirectoryError(path.to_os_specific())

        files = []

        for file in VFS.scan_directory(path):
            if (path := file.get_filename()).is_directory():
                if recursive:
                    files.extend(
                        self.load_directory(
                            path,
                            recursive = recursive,
                            extensions = extensions,
                            ))
                else:
                    continue
            elif path.is_regular_file():
                if extensions and (path.get_extension() not in extensions):
                    continue
                else:
                    files.append(self.load_file(path))
            else:
                raise OSError(f'invalid file: {file!r}')

        return files
