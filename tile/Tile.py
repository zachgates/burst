from panda3d import core as p3d


class Tile(p3d.Texture):

    _NAMEPLATE = 'tex:{0}:ref:{1}'

    @classmethod
    def getName(cls, tileset: 'TileSet', index: int) -> str:
        return cls._NAMEPLATE.format(tileset.name, index)

    def __init__(self, name: str, index: int = 0):
        super().__init__(name)
        self.__idx = index

    def __hash__(self):
        return self.name

    @property
    def index(self):
        return self.__idx
