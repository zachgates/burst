from xml.etree import ElementTree

from ..base import File, FileError


class XMLFile(File, ElementTree.ElementTree):

    _fext = '.xml'

    def __init__(self, abspath, ignore_ext=False):
        File.__init__(self, abspath)

        if not ignore_ext:
            if self.fext != XMLFile._fext:
                raise FileError('file "%s" has invalid extension: "%s"' % (
                    self.fname,
                    self.fext))

        self._root = ElementTree.fromstring(self.read())

    def __str__(self):
        return '<%s %s>' % (self.name, self.fname)

    @property
    def name(self):
        return self._root.tag
