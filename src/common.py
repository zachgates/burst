import os

from . import constants
from .base import File, FileError
from .xmllib.base import XMLFile

from panda3d.core import Filename


class FileManager(object):

    _root = ''

    def __init__(self, root=None):
        object.__init__(self)
        self._root = str(root or FileManager._root or vfs.getCwd())
        self._ext = ''

    def getRoot(self):
        return self._root

    def setRoot(self, path):
        self._root = str(path)

    def getRestrictToExt(self):
        return self._ext

    def setRestrictToExt(self, fext):
        self._ext = str(fext)

    def find(self, relpath):
        return vfs.findFile(relpath, self._root)

    def loadDirectory(self, relpath, filesOnly=False, foldersOnly=False):
        rootRelpath = os.path.join(self._root, relpath)
        virtualLink = Filename(rootRelpath)

        if virtualLink and virtualLink.isDirectory():
            for virtualFile in vfs.scanDirectory(virtualLink):
                if filesOnly and not virtualFile.isRegularFile():
                    continue
                elif foldersOnly and not virtualFile.isDirectory():
                    continue
                else:
                    fname, fext = os.path.splitext(str(virtualFile))
                    if self._ext and fext != self._ext:
                        continue
                    else:
                        fpath = os.path.join(self._root, relpath, fname)
                        yield Filename(fpath + fext)

    def loadFile(self, virtualFile):
        if virtualFile:
            return File(virtualFile.getFilename())
        else:
            return None

    def loadXML(self, virtualFile):
        try:
            with XMLFile(virtualFile.getFilename()) as fobj:
                return fobj
        except FileError as e:
            return None
