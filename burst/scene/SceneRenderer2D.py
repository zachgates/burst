__all__ = [
    'SceneRenderer2D', 'Scene2D',
]


import typing

import panda3d.core as p3d

from burst.control import File
from burst.core import Tile, TileSet
from burst.scene import SceneRendererBase


class SceneRenderer2D(SceneRendererBase):

    def pack(self):
        dg = super().pack()
        dg.add_fixed_string(self.tiles.pixel.get_name(), 0xFF)
        dg.add_uint16(self.tiles.pixel.get_x_size())
        dg.add_uint16(self.tiles.pixel.get_y_size())
        dg.add_blob32(self.tiles.pixel.buffer.get_data())
        dg.add_uint16(self.tiles.rules.tile_size.x)
        dg.add_uint16(self.tiles.rules.tile_size.y)
        dg.add_uint16(self.tiles.rules.tile_run.x)
        dg.add_uint16(self.tiles.rules.tile_run.y)
        dg.add_uint16(self.tiles.rules.tile_offset.x)
        dg.add_uint16(self.tiles.rules.tile_offset.y)
        return dg

    def __init__(self,
                 title: str,
                 resolution: tuple,
                 tiles: TileSet,
                 ):

        super().__init__(title, resolution)
        self.tiles = tiles
        self._cm = p3d.CardMaker(f'{self.tiles.name}')
        self._cm.set_frame_fullscreen_quad()

    def get_tile(self, /, *, row: int, column: int) -> Tile:
        return self.tiles.get(p3d.LPoint2i(row, column))

    def get_tile_card(self, /, *, row: int, column: int) -> p3d.NodePath:
        np = base.hidden.attach_new_node(self._cm.generate())
        np.set_texture(tile := self.get_tile(row = row, column = column))
        np.set_python_tag('tile', tile)
        np.node().set_name(tile.get_name())
        return np


Scene2D = SceneRenderer2D
