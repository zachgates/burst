from xml.etree import ElementTree

from .base import File


class XMLFile(File):

    _fext = 'xml'

    def __init__(self, pandaFilename, **kwargs):
        File.__init__(self, pandaFilename, **kwargs)
        self.__root = None

    def __repr__(self):
        return '<[%s] %s>' % (self.fname, self.name)

    @property
    def name(self):
        return self.tree.tag

    @property
    def tree(self):
        if self.__root is None: self.read()
        return self.__root

    def read(self):
        content = File.read(self)
        self.__root = ElementTree.fromstring(content)
        return content
