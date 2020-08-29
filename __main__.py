import builtins

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from .core.TileSet import TileSet


class BurstApp(ShowBase):

    def __init__(self, f_name, **rules):
        super().__init__()
        self.__tile_pool = TileSet(f_name, **rules)
        self.__tile_card = p3d.CardMaker(f'{self.tileset.name}')
        self.__tile_card.setFrameFullscreenQuad()

    @property
    def tileset(self):
        return self.__tile_pool

    def make(self, index: int) -> p3d.NodePath:
        """
        Returns a NodePath with the Texture generated from the Tile at the
        supplied index of the TileSet.
        """
        tile = aspect2d.attachNewNode(self.__tile_card.generate())
        tile.setTexture(self.tileset.loadTexture(index))
        tile.node().setName(f'{index}_{self.__tile_card.name}')
        return tile

    def run(self):
        self.make(278)
        super().run()


builtins.burst = BurstApp('tilesheet.png', size = 16, run = 32, offset = 1)
burst.run()
