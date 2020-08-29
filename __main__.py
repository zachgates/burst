import builtins

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from .core.TileSet import TileSet


class BurstApp(ShowBase):

    def __init__(self, f_name, **rules):
        super().__init__()
        self.__tile_pool = TileSet(f_name, **rules)
        self.__tile_card = p3d.CardMaker(f'tile-maker:{self.tileset.name}')
        self.__tile_card.setFrameFullscreenQuad()

    @property
    def tileset(self):
        return self.__tile_pool

    def createTile(self, index: int) -> p3d.NodePath:
        """
        Returns a NodePath with the Texture generated from the Tile at the
        supplied index of the TileSet.
        """
        tex = self.tileset.loadTexture(index)
        tile = self.__tile_card.generate()
        tile.setName(tex.getName())
        tileNP = aspect2d.attachNewNode(tile)
        tileNP.setTexture(tex)
        return tileNP

    def run(self):
        np = self.createTile(-5)
        super().run()


builtins.burst = BurstApp('fake_5x5.png', size = 5, run = 5, offset = 0)
burst.run()
