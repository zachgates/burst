import builtins

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from .core.TileCache import TileCache
from .core.TileSet import TileSet


class BurstApp(ShowBase):

    def __init__(self, f_name, **rules):
        super().__init__()

        f_path = p3d.Filename(f_name)
        self.__cache = TileCache(f_path)
        self.__tileset = TileSet(f_path, **rules)

        self.__tile_card = p3d.CardMaker(f'{self.tileset.name}')
        self.__tile_card.setFrameFullscreenQuad()

    @property
    def cache(self) -> TileCache:
        return self.__cache

    @property
    def tileset(self) -> TileSet:
        return self.__tileset

    def make_tile(self, index: int) -> p3d.NodePath:
        """
        Returns a NodePath with the Texture generated from the Tile at the
        supplied index of the TileSet.
        """
        tile = hidden.attachNewNode(self.__tile_card.generate())
        tile.setTexture(self.tileset.loadTexture(index))
        tile.node().setName(f'{index}_{self.__tile_card.name}')
        return tile

    def run(self):
        seqNode = p3d.SequenceNode('sprite')
        for n in (275, 279, 277, 278):
            seqNode.addChild(self.make_tile(n).node())
        seqNode.setFrameRate(12)
        seqNode.pingpong(True)
        seqNP = aspect2d.attachNewNode(seqNode)
        super().run()


builtins.burst = BurstApp('tilesheet.png', size = 16, run = 32, offset = 1)
burst.run()
