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

from burst.core import PixelMatrix, RuleBase, Rule2D


class Tile(p3d.Texture):

    def __init__(self, name: str, size: Rule2D):
        super().__init__(name)

        self.__size = size
        self.__data = None

        self.setup_2d_texture(
            self.__size.x,
            self.__size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )

    def get_ram_image(self) -> np.ndarray:
        if hash(super().get_ram_image()) == hash(self.__data):
            return np.reshape(self.__data, (self.__size.x, self.__size.y, 4))
        else:
            raise Exception('ram image changed')

    def get_ram_image_as(self, format):
        raise NotImplementedError()

    def set_ram_image(self, data: p3d.PTAUchar):
        self.__data = data
        super().set_ram_image(self.__data)

    def set_ram_image_as(self, data, format):
        raise NotImplementedError()

    def set_blend(self, color: p3d.LColor):
        for row in self.get_ram_image():
            for cell in row:
                if tuple(cell) == color:
                    cell[3] = 0

    def set_blend_off(self):
        for row in self.get_ram_image():
            for cell in row:
                cell[3] = 255


class TileSet(dict):

    _NAMEPLATE = '{0}_{1}_{2}'

    @dataclasses.dataclass(init = False)
    class Rules(RuleBase):
        """
        Three rules defining the parameters of a TileSet.
        """
        tile_size: Rule2D = Rule2D(1, 1)
        tile_run: Rule2D = Rule2D(1, 1)
        tile_offset: Rule2D = Rule2D(0, 0)

    def __init__(self, path: str, **rules):
        super().__init__()

        if path:
            self.atlas = base.loader.load_texture(path)
            self.pixel = PixelMatrix(self.atlas)
            self.rules = TileSet.Rules(**rules)
        else:
            self.atlas = None
            self.pixel = None
            self.rules = TileSet.Rules()

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

    @property
    def name(self) -> str:
        """
        Returns the name of the TileSet.
        """
        return f"{self.atlas.get_name() if self.atlas else 'empty'}"

    def _get_child_name(self, point: p3d.LPoint2i) -> str:
        """
        Returns the name for the given cell in the TileSet.
        """
        return self._NAMEPLATE.format(self.name, point.x, point.y)

    def __draw(self, index: int) -> list:
        """
        Returns the Texture data of the given Tile as a PTAUchar.
        """
        px_rows = []
        if index:
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
                        * self.pixel.width
                        )
                     ),
                y = ((col - 1)
                     * (self.rules.tile_size.x
                        + self.rules.tile_offset.x
                        )
                     ),
                )

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

    def get(self, point: p3d.LPoint2i) -> p3d.Texture:
        """
        Returns the Texture for the given cell in the TileSet.
        """
        if (name := self._get_child_name(point)) in self:
            return self[name]
        else:
            index = ((point.x - 1) * self.rules.tile_run.x) + point.y
            tile = self[name] = Tile(name, self.rules.tile_size)
            tile.set_magfilter(p3d.Texture.FT_nearest)
            tile.set_ram_image(self.__draw(index))
            return tile
