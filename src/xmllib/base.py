from xml.etree import ElementTree

from ..base import File, FileError


UNKNOWN_TAG = '?'


class XMLFile(File, ElementTree.ElementTree):

    _fext = 'xml'

    def __init__(self, pandaFilename, ignore_ext=False):
        File.__init__(self, pandaFilename)
        self._root = None

        if not ignore_ext:
            if self.fext != XMLFile._fext:
                raise FileError('file "%s" has invalid extension: "%s"' % (
                    self.fname,
                    self.fext))

    def __str__(self):
        return '<%s__%s>' % (self.name, self.fname)

    @property
    def name(self):
        if self._root:
            return self._root.tag
        else:
            return UNKNOWN_TAG

    @property
    def tree(self):
        if self._root is None:
            self.read()

        return self._root

    def _read(self):
        content = File._read(self)
        self._root = ElementTree.fromstring(content)
