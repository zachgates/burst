import os

from . import constants


class FileError(IOError):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class File(object):

    _fext = ''

    def __init__(self, virtualFile):
        object.__init__(self)
        self._vFile = virtualFile
        self._fname = self._vFile.getBasenameWoExtension()
        self._fext = self._vFile.getExtension()
        self._content = None

    def __str__(self):
        return self.read()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        pass

    @property
    def fname(self):
        return self._fname

    @property
    def fext(self):
        return self._fext

    def __read(self):
        with open(self._vFile.getFilename(), 'r') as fobj:
            return fobj.read()

    def read(self):
        return self._content or self.__read()
