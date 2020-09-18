from panda3d import core as p3d

from ..core import PixelMatrix
from ..tile import TileSet


class Scene2D(object):

    @classmethod
    def makeAtlas(cls, name: str, data: bytes, size: tuple):
        tex = p3d.Texture()
        tex.setup2dTexture(*size, p3d.Texture.TUnsignedByte, p3d.Texture.FRgba)
        tex.setFullpath(name)
        tex.setName(name)
        tex.setRamImage(data)
        p3d.TexturePool.addTexture(tex)

    def __init__(self,
                 scene_name: str, scene_res: tuple,
                 atlas_name: str, atlas_data: bytes, atlas_size: tuple,
                 atlas_rules: dict):
        super().__init__()
        self.adjustWindow(scene_name, scene_res)
        self.makeAtlas(atlas_name, atlas_data, atlas_size)
        self.tiles = TileSet(atlas_name, **atlas_rules)

    def adjustWindow(self, scene_name: str, scene_res: tuple):
        prop = p3d.WindowProperties()
        prop.setTitle(scene_name)
        prop.setSize(scene_res)
        base.win.requestProperties(prop)

    def makeTile(self, index: int) -> p3d.NodePath:
        # TEMP
        if not hasattr(self, '_cm'):
            self._cm = p3d.CardMaker(f'{self.tiles.name}')
            self._cm.setFrameFullscreenQuad()

        tile = hidden.attachNewNode(self._cm.generate())
        tile.setTexture(self.tiles.get(index))
        tile.node().setName(f'{index}_{self._cm.name}')
        return tile
