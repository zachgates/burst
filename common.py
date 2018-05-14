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
            file_ = self.getFile(relpath)
            fname = file_.getFilename().getBasenameWoExtension()
            yield (fname, file_)

    def loadXML(self, file_):
        try:
            with XMLFile(file_.getFilename()) as fobj:
                return fobj
        except FileError as e:
            pass


def load_xml_files():
    files = []
    types = set()

    for file_ in vfs.scanDirectory(base.fileManager.ROOT):
        print(file_)
        if file_.getFilename().getExtension() == 'xml':
            xml = base.fileManager.loadXML(file_)
            if xml:
                files.append(xml)
                types.add(xml.name)

    return {type_: [fobj for fobj in files if fobj.name == type_]
            for type_ in types}
