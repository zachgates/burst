__all__ = [
    'Tile',
    'TileSet',
]


import burst
import dataclasses
import math
import numpy as np
import typing

import panda3d.core as p3d

from burst.core import PixelMatrix, TextureFile
from burst import cext


_CM = p3d.CardMaker('cm')
_CM.set_frame_fullscreen_quad()


class Tile(p3d.Texture):

    def modify_ram_image(self):
        return np.reshape(
            super().modify_ram_image(),
            (self.get_y_size(), self.get_x_size(), 4),
            )

    def set_blend(self, color: p3d.LColor):
        for row in self.modify_ram_image():
            for cell in row:
                if tuple(cell[0:3]) == color.get_xyz():
                    cell[3] = 0

    def set_blend_off(self, color: typing.Optional[p3d.LColor] = None):
        for row in self.modify_ram_image():
            for cell in row:
                if ((color is None)
                    or (color and (tuple(cell[0:3]) == color.get_xyz()))
                    ):
                    cell[3] = 255


class TileSet(PixelMatrix):

    _NAMEPLATE = '{0}_{1}_{2}'

    @dataclasses.dataclass
    class Rules(object):
        """
        Three rules defining the parameters of a TileSet.
        """

        tile_size: p3d.LVector2i = dataclasses.field(default_factory = p3d.LVector2i)
        tile_run: p3d.LVector2i = dataclasses.field(default_factory = p3d.LVector2i)
        tile_offset: p3d.LVector2i = dataclasses.field(default_factory = p3d.LVector2i)

        def read_datagram(self, dgi: p3d.DatagramIterator):
            for field in self.__dataclass_fields__:
                vec = getattr(self, field)
                vec.read_datagram(dgi)

        def write_datagram(self, dg: p3d.Datagram):
            for field in self.__dataclass_fields__:
                vec = getattr(self, field)
                vec.write_datagram(dg)

    def __init__(self, texture: p3d.Texture, rules: Rules):
        super().__init__(texture.get_name())
        self.rules = rules

        self.setup_2d_texture(
            texture.get_x_size(),
            texture.get_y_size(),
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )

        self.set_fullpath(texture.get_fullpath())
        self.set_ram_image(texture.get_ram_image())

    def __draw(self, index: int) -> list:
        """
        Returns the Texture data of the given Tile as a PTAUchar.
        """
        px_rows = []

        tile_count = (self.rules.tile_run.x * self.rules.tile_run.y)
        if not ((index > 0) and (index <= tile_count)):
            raise ValueError(f'index out of range(0, {tile_count + 1})')

        row = math.ceil(index / self.rules.tile_run.y)
        col = ((index - 1) % self.rules.tile_run.x) + 1
        off = p3d.LVector2i(
            x = ((row - 1)
                 * ((self.rules.tile_size.x * self.rules.tile_size.y)
                    * self.rules.tile_run.y
                    + (self.rules.tile_run.x - 1)
                    * self.rules.tile_size.y
                    * self.rules.tile_offset.x
                    + self.rules.tile_offset.y
                    * self.get_x_size()
                    )),
            y = ((col - 1)
                 * (self.rules.tile_size.x
                    + self.rules.tile_offset.x
                    )))

        for row in range(self.rules.tile_size.y):
            offset = (off.x + off.y + 1)
            off.y += ((self.rules.tile_run.x * self.rules.tile_size.x)
                      + (self.rules.tile_run.x - 1)
                      * self.rules.tile_offset.x
                      )

            px_rows.append([self.get_pixel(offset + col)
                            for col in range(self.rules.tile_size.x)
                            ])

        px_data = bytearray()
        for row in reversed(px_rows):
            for cell in row:
                px_data.extend(cell)

        return p3d.PTAUchar(px_data)

    def make_tile(self, /, *, row: int, column: int) -> Tile:
        """
        Returns a Tile for the given cell in the TileSet.
        """
        index = ((row - 1) * self.rules.tile_run.x) + column
        tile = Tile(self._NAMEPLATE.format(self.get_name(), row, column))
        tile.setup_2d_texture(
            self.rules.tile_size.x,
            self.rules.tile_size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )
        tile.set_magfilter(p3d.Texture.FT_nearest)
        tile.set_ram_image(self.__draw(index))
        return tile

    def make_tile_card(self, /, *, row: int, column: int) -> p3d.NodePath:
        global _CM
        np = base.hidden.attach_new_node(_CM.generate())
        np.set_texture(tile := self.make_tile(row = row, column = column))
        np.node().set_name(tile.get_name())
        np.node().set_python_tag('tile', tile)
        return np
