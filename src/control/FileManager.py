#!/usr/local/bin/python3.9

import pathlib
import re
import sys

from typing import Iterator, Optional, Union

from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject

from .. import core


VFS = p3d.VirtualFileSystem.get_global_ptr()

SEACH_PATH = p3d.DSearchPath()
for path in sys.path:
	SEACH_PATH.append_directory(path)


class FileManager(DirectObject, core.ExtensionsMixin):

    def __init__(self, /, *, extensions: Optional[list[str]] = ()):
        DirectObject.__init__(self)
        core.ExtensionsMixin.__init__(self, extensions)

    def find_file(self, path: Union[str, pathlib.Path]) -> p3d.VirtualFile:
        """
        Attempts to find the given path, creating a VirtualFile pointer.
        """
        if isinstance(path, (str, pathlib.Path)):
            return VFS.find_file(path, SEACH_PATH)
        else:
            raise TypeError(f'expected string or pathlib.Path for path')

    findFile = find_file

    def load_file(self,
                  path: Union[str, pathlib.Path, p3d.VirtualFile],
                  ) -> core.File:
        """
        Attempts to create a File object from its VirtualFile pointer.
        """
        if isinstance(path, p3d.VirtualFile):
            vfile = path
        else:
            vfile = self.find_file(path)

        fext = vfile.get_filename().get_extension()

        if (fext in self.extensions) or not self.extensions:
            return core.File(vfile)
        else:
            raise ValueError(f'cannot load filetype: {fext}')

    loadFile = load_file

    def load_directory(self,
                       path: Union[str, pathlib.Path],
                       /, *,
                       recursive: bool = False,
                       extensions: Union[list, tuple, set] = (),
                       ) -> list[core.File]:
        """
        Attempts to find and load a directory of Files from the given path.
        A recursive loading flag may also be supplied, and/or a group of
        extensions to use as a filter.
        """
        if isinstance(path, p3d.VirtualFile):
            vfile = path
        else:
            vfile = self.find_file(path)

        if not vfile.is_directory():
            raise NotADirectoryError(vfile.get_filename().to_os_specific())

        if isinstance(extensions, (list, tuple, set)):
            extensions = core.validate_extensions(*extensions)
        else:
            raise TypeError('expected list/tuple/set for extensions')

        files = []

        for vfile in VFS.scan_directory(vfile.get_filename()):
            if vfile.is_directory() and recursive:
                files += self.load_directory(
                    vfile,
                    recursive = recursive,
                    extensions = extensions,
                    )
            elif vfile.is_regular_file():
                fext = vfile.get_filename().get_extension()
                if extensions and (not fext in extensions):
                    continue
                else:
                    files.append(self.load_file(vfile))
            else:
                raise OSError(f'invalid file: {vfile!r}')

        return files

    loadDirectory = load_directory
