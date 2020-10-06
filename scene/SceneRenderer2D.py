"""
The primary rendering logic of a scene, directly related to the User Interface.
The file includes both the SceneRenderer2D object, and a secondary reference to
the same, Scene2D.
"""


__all__ = ['SceneRenderer2D', 'Scene2D']


class SceneRenderer2D(object):

    @classmethod
    def make_atlas(cls, name: str, data: bytes, size: tuple):
        tex = burst.p3d.Texture()
        tex.setup2dTexture(
            *size,
            burst.p3d.Texture.TUnsignedByte,
            burst.p3d.Texture.FRgba)
        tex.setFullpath(name)
        tex.setName(name)
        tex.setRamImage(data)
        burst.p3d.TexturePool.addTexture(tex)

    def __init__(self,
                 scene_name: str, scene_res: tuple,
                 atlas_name: str, atlas_data: bytes, atlas_size: tuple,
                 atlas_rules: dict):
        super().__init__()
        self.adjust_window(scene_name, scene_res)
        self.make_atlas(atlas_name, atlas_data, atlas_size)
        self.tiles = burst.tile.TileSet(atlas_name, **atlas_rules)

    def adjust_window(self, scene_name: str, scene_res: tuple):
        prop = burst.p3d.WindowProperties()
        prop.setTitle(scene_name)
        prop.setSize(scene_res)
        base.win.requestProperties(prop)

    def make_tile(self, index: int) -> burst.p3d.NodePath:
        # TEMP
        if not hasattr(self, '_cm'):
            self._cm = burst.p3d.CardMaker(f'{self.tiles.name}')
            self._cm.setFrameFullscreenQuad()

        np = hidden.attachNewNode(self._cm.generate())
        np.setTexture(self.tiles.get(index))
        np.node().setName(f'{index}_{self._cm.name}')
        return np


Scene2D = SceneRenderer2D
