import builtins

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from .tile.TileCache import TileCache
from .tile.TileSet import TileSet


class BurstApp(ShowBase):

    def __init__(self):
        super().__init__()
        self.__root = p3d.Filename(p3d.Filename(__file__).getDirname())
        self.__cache = None
        self.__tile_set = None
        self.__tile_gen = None

    def init(self, f_name, **rules):
        f_name = p3d.Filename(f_name)
        self.__cache = TileCache(f_name)
        self.__tile_set = TileSet(f_name, **rules)
        self.__tile_gen = p3d.CardMaker(f'{self.tileset.name}')
        self.__tile_gen.setFrameFullscreenQuad()

    @property
    def root(self) -> p3d.Filename:
        return self.__root

    @property
    def cache(self) -> TileCache:
        return self.__cache

    @property
    def tileset(self) -> TileSet:
        return self.__tile_set

    def make_tile(self, index: int) -> p3d.NodePath:
        """
        Returns a NodePath with the Texture generated from the Tile at the
        supplied index of the TileSet.
        """
        tile = hidden.attachNewNode(self.__tile_gen.generate())
        tile.setTexture(self.tileset.loadTexture(index))
        tile.node().setName(f'{index}_{self.__tile_gen.name}')
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
burst.init('tile/tilesheet.png', tile_size = 16, tile_run = 32, tile_offset = 1)
burst.run()
