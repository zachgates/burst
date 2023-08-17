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

from burst.core import PixelMatrix


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


class TileSet(dict):

    _NAMEPLATE = '{0}_{1}_{2}'

    @dataclasses.dataclass
    class Rules(object):
        """
        Three rules defining the parameters of a TileSet.
        """
        tile_size: p3d.LVector2i
        tile_run: p3d.LVector2i
        tile_offset: p3d.LVector2i

    def __init__(self,
                 path: str,
                 size: p3d.LVector2i,
                 data: bytes,
                 **rules,
                 ):

        self.rules = TileSet.Rules(**rules)

        self.pixel = PixelMatrix(path)
        self.pixel.setup_2d_texture(
            size.x,
            size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )

        self.pixel.set_fullpath(path)
        self.pixel.set_ram_image(data)

    @property
    def name(self) -> str:
        """
        Returns the name of the atlas of the TileSet.
        """
        return self.pixel.get_name()

    @property
    def size(self) -> int:
        """
        Returns the size, in pixels, of the tiles in the TileSet.
        """
        return (self.rules.tile_size.x * self.rules.tile_size.y)

    @property
    def count(self) -> int:
        """
        Returns the number of tiles in the TileSet.
        """
        return (self.rules.tile_run.x * self.rules.tile_run.y)

    def _get_tile_name(self, point: p3d.LPoint2i) -> str:
        """
        Returns the name for the given cell in the TileSet.
        """
        return self._NAMEPLATE.format(self.pixel.name, point.x, point.y)

    def __draw(self, index: int) -> list:
        """
        Returns the Texture data of the given Tile as a PTAUchar.
        """
        px_rows = []

        if not ((index > 0) and (index <= self.count)):
            raise ValueError(f'index out of range(0, {self.count + 1})')

        row = math.ceil(index / self.rules.tile_run.y)
        col = ((index - 1) % self.rules.tile_run.x) + 1
        off = p3d.LVector2i(
            x = ((row - 1)
                 * (self.size
                    * self.rules.tile_run.y
                    + (self.rules.tile_run.x - 1)
                    * self.rules.tile_size.y
                    * self.rules.tile_offset.x
                    + self.rules.tile_offset.y
                    * self.pixel.get_x_size()
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

            px_rows.append([self.pixel.get(offset + col)
                            for col in range(self.rules.tile_size.x)])

        px_data = bytearray()
        for row in reversed(px_rows):
            for cell in row:
                px_data.extend(cell)

        return p3d.PTAUchar(px_data)

    def get(self, point: p3d.LPoint2i) -> Tile:
        """
        Returns a Tile for the given cell in the TileSet.
        """
        index = ((point.x - 1) * self.rules.tile_run.x) + point.y
        tile = Tile(self._get_tile_name(point))
        tile.setup_2d_texture(
            self.rules.tile_size.x,
            self.rules.tile_size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )
        tile.set_magfilter(p3d.Texture.FT_nearest)
        tile.set_ram_image(self.__draw(index))
        return tile
