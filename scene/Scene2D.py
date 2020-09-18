from panda3d import core as p3d

from ..core import PixelMatrix
from ..tile import TileSet


class Scene2D(object):

    @classmethod
    def make_atlas(cls, data: bytes, size: tuple) -> p3d.Texture:
        tex = p3d.Texture()
        tex.setup2dTexture(*size, p3d.Texture.TUnsignedByte, p3d.Texture.FRgba)
        tex.setRamImage(data)
        return tex

    def __init__(self,
                 scene_name: str, scene_size: tuple,
                 atlas_data: bytes, atlas_size: tuple, atlas_rules: dict):
        prop = p3d.WindowProperties()
        prop.setTitle(scene_name)
        prop.setSize(scene_size)
        base.win.requestProperties(prop)

        self.tiles = TileSet(None, **atlas_rules)
        self.tiles.atlas = self.make_atlas(atlas_data, atlas_size)
        self.tiles.pixel = PixelMatrix(self.tiles.atlas)

    def make_tile(self, index: int) -> p3d.NodePath:
        # TEMP
        if not hasattr(self, '_cm'):
            self._cm = p3d.CardMaker(f'{self.tiles.name}')
            self._cm.setFrameFullscreenQuad()

        tile = hidden.attachNewNode(self._cm.generate())
        tile.setTexture(self.tiles.get(index))
        tile.node().setName(f'{index}_{self._cm.name}')
        return tile
