from panda3d.core import Texture

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileTexture(Texture):

    def __init__(self, parent, name, width, height):
        super().__init__(name)
        self.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba)
        self._parent = parent


class Tile(DirectObject):

    def __init__(self, name):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name
