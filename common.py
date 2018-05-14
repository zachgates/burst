import os

from . import constants
from .base import FileError
from .xmllib.base import XMLFile


class FileManager(object):

    ROOT = ''

    def __init__(self, root=''):
        object.__init__(self)
        self.__setRoot(root or vfs.getCwd())

    def __setRoot(self, abspath):
        self.ROOT = str(abspath)

    def getFile(self, relpath):
        return vfs.findFile(relpath, ROOT)

    def getFiles(self, relpaths):
        for relpath in relpaths:
            virtualFile = self.getFile(relpath)
            yield File(virtualFile.getFilename())

    def loadXML(self, virtualFile):
        try:
            with XMLFile(virtualFile.getFilename()) as fobj:
                return fobj
        except FileError as e:
            pass
