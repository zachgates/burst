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
        self.tiles.pixel.size.write_datagram(dg)
        dg.add_blob32(self.tiles.pixel.get_ram_image().get_data())
        self.tiles.rules.tile_size.write_datagram(dg)
        self.tiles.rules.tile_run.write_datagram(dg)
        self.tiles.rules.tile_offset.write_datagram(dg)
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
        np.node().set_name(tile.get_name())
        np.node().set_python_tag('tile', tile)
        return np


Scene2D = SceneRenderer2D
