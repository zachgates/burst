import os

from . import constants
from .base import File, FileError
from .xmllib.base import XMLFile

from panda3d.core import ConfigVariableString


class FileManager(object):

    ROOT = ''

    def __init__(self, root=None):
        object.__init__(self)
        self.ROOT = str(root or FileManager.ROOT or vfs.getCwd())

    @property
    def root(self):
        return self.ROOT

    @property
    def model_ext(self):
        return ConfigVariableString('default-model-extension').getValue()

    def find(self, relpath):
        return vfs.findFile(relpath, self.root)

    def scan(self, relpath, filesOnly=False, foldersOnly=False):
        for virtualFile in vfs.scanDirectory(relpath):
            if filesOnly and not virtualFile.isRegularFile():
                continue
            elif foldersOnly and not virtualFile.isDirectory():
                continue
            else:
                yield virtualFile

    def loadDirectory(self, virtualLink, modelsOnly=None):
        if virtualLink and virtualLink.isDirectory():
            for virtualFile in virtualLink.scanDirectory().getFiles():
                fname = virtualFile.getFilename()
                if modelsOnly and fname.getExtension() != self.model_ext[1:]:
                    continue
                else:
                    yield fname

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
