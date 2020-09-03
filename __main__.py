import builtins

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from .tiles.TileCache import TileCache
from .tiles.TileSet import TileSet


class BurstApp(ShowBase):

    def __init__(self):
        super().__init__()
        self.__root = p3d.Filename(p3d.Filename(__file__).getDirname())
        self.__tileset = None

    def init(self, f_name, **rules):
        self.__tileset = TileSet(p3d.Filename(f_name), **rules)
        self.__tile_card = p3d.CardMaker(f'{self.tileset.name}')
        self.__tile_card.setFrameFullscreenQuad()

    @property
    def root(self) -> p3d.Filename:
        return self.__root

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


builtins.burst = BurstApp()
burst.init('tilesheet.png', tile_size = 16, tile_run = 32, tile_offset = 1)
burst.run()
