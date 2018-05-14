import os

from . import constants


class FileError(IOError):

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class File(object):

    _fext = ''

    def __init__(self, pandaFilename):
        object.__init__(self)
        self._fpath = str(pandaFilename)
        self._fname = str(pandaFilename.getBasenameWoExtension())
        self._fext = str(pandaFilename.getExtension())
        self._content = None

    def __str__(self):
        return '%s.%s' % (self.fname, self.fext)

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

    def _read(self):
        with open(self._fpath, 'r') as fobj:
            return fobj.read()

    def read(self):
        return self._content or self._read()
