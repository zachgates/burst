from panda3d import core as p3d
from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def __init__(self, f_name, **rules):
        super().__init__()
        self.__tile_set = burst.load_tileset(f_name, **rules)
        self.__tile_gen = p3d.CardMaker(f'{self.__tile_set.name}')
        self.__tile_gen.setFrameFullscreenQuad()

    def make_tile(self, index: int) -> p3d.NodePath:
        tile = hidden.attachNewNode(self.__tile_gen.generate())
        tile.setTexture(self.__tile_set.get(index))
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


app = TestApp('tilesheet.png', tile_size = 16, tile_run = 32, tile_offset = 1)
app.run()
