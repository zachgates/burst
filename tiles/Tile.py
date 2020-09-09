import uuid

from panda3d import core as p3d


class Tile(p3d.Texture):

    _NAMEPLATE = 'tex:{0}:ref:{1}'

    @classmethod
    def getName(cls, index: int) -> str:
        return cls._NAMEPLATE.format(burst.tileset.name, index)

    @classmethod
    def getPath(self, index: int):
        root = p3d.Filename(burst.tileset.atlas.getFullpath())
        hv = p3d.HashVal()
        hv.hashFile(root)
        base = uuid.UUID(hv.asHex())
        path = f'{uuid.uuid3(base, hex(index)).hex}.tile'
        return p3d.Filename(root.getFullpathWoExtension(), path)

    def __init__(self, index: int = 0):
        super().__init__(self.getName(index))
        self.__idx = index

    @property
    def index(self):
        return self.__idx
