__all__ = ['SceneRenderer2D', 'Scene2D']


import panda3d.core as p3d

from . import SceneRendererBase


class SceneRenderer2D(SceneRendererBase):

    @classmethod
    def make_atlas(cls, name: str, data: bytes, size: tuple):
        tex = p3d.Texture()
        tex.setup_2d_texture(
            *size,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba)
        tex.set_fullpath(name)
        tex.set_name(name)
        tex.set_ram_image(data)
        p3d.TexturePool.add_texture(tex)

    def __init__(self,
                 title: str, resolution: tuple,
                 atlas_name: str, atlas_data: bytes, atlas_size: tuple,
                 atlas_rules: dict,
                 ):
        super().__init__(title, resolution)
        self.make_atlas(atlas_name, atlas_data, atlas_size)
        self.tiles = burst.core.TileSet(atlas_name, **atlas_rules)

    def make_tile(self, index: int) -> p3d.NodePath:
        # TEMP
        if not hasattr(self, '_cm'):
            self._cm = p3d.CardMaker(f'{self.tiles.name}')
            self._cm.set_frame_fullscreen_quad()

        np = hidden.attach_new_node(self._cm.generate())
        np.set_texture(self.tiles.get(index))
        np.node().set_name(f'{index}_{self._cm.name}')
        return np


Scene2D = SceneRenderer2D
