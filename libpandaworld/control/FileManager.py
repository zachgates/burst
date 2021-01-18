#!/usr/local/bin/python3.9

import pathlib
import re
import sys

from typing import Container, Iterable, Union

from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject

from ..core import ExtensionsMixin, File, validate_extensions


VFS = p3d.VirtualFileSystem.get_global_ptr()

SEARCH_PATH = p3d.DSearchPath()
for path in sys.path:
    SEARCH_PATH.append_directory(path)


class FileManager(DirectObject, ExtensionsMixin):

    def __init__(self, *extensions: str):
        DirectObject.__init__(self)
        ExtensionsMixin.__init__(self, *extensions)

    def scan_path(self,
                  path: Union[str, pathlib.Path, p3d.Filename],
                  ) -> p3d.Filename:
        """
        Attempts to find the given path, creating a VirtualFile pointer.
        """
        if isinstance(path, p3d.Filename):
            path = path.to_os_specific()

        if isinstance(path, (str, pathlib.Path)):
            if (file := VFS.find_file(path, SEARCH_PATH)) is not None:
                return file.get_filename()
            else:
                raise FileNotFoundError(path)
        else:
            raise TypeError('expected string, pathlib.Path, '
                            'or panda3d.core.Filename for path')

    def load_file(self, path: p3d.Filename) -> File:
        """
        Attempts to create a File object from its VirtualFile pointer.
        """
        path = self.scan_path(path)
        if (path.get_extension() in self.extensions) or not self.extensions:
            return File(path)
        else:
            raise ValueError(f'cannot load filetype: {path.get_extension()}')

    def load_directory(self, path, /, *,
                       recursive: bool = False,
                       extensions: Iterable = (),
                       ) -> list[File]:
        """
        Attempts to find and load a directory of Files from the given path.
        A recursive loading flag may also be supplied, and/or a group of
        extensions to use as a filter.
        """
        if isinstance(extensions, Container):
            extensions = validate_extensions(*extensions)

        if not (path := self.scan_path(path)).is_directory():
            raise NotADirectoryError(path.to_os_specific())

        files = []

        for file in VFS.scan_directory(path):
            path = file.get_filename()
            if path.is_directory() and recursive:
                files += self.load_directory(
                    path,
                    recursive = recursive,
                    extensions = extensions,
                    )
            elif path.is_regular_file():
                if extensions and (path.get_extension() not in extensions):
                    continue
                else:
                    files.append(self.load_file(path))
            else:
                raise OSError(f'invalid file: {vfile!r}')

        return files
