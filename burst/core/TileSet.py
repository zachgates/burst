__all__ = [
    'TileSet',
]


import burst
import dataclasses
import math
import numpy as np
import typing

import panda3d.core as p3d

from burst.core import RuleBase, Rule2D


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
            self.rules = self.Rules(**rules)
        else:
            self.atlas = None
            self.rules = TileSet.Rules()

        if self.atlas and self.atlas.has_ram_image():
            width, height = (self.atlas.get_x_size(), self.atlas.get_y_size())
            self.__data = bytearray(self.atlas.get_ram_image_as('BGRA'))
        else:
            width = height = 1
            self.__data = bytearray(4)

        self.__size = Rule2D(width, height)
        self._data = np.reshape(self.__data, (height, width, 4))

    @property
    def width(self) -> int:
        return self.__size.x

    @property
    def height(self) -> int:
        return self.__size.y

    @property
    def data(self) -> bytes:
        return bytes(self.__data)

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

    def _get_child_name(self, cell: p3d.LPoint2i) -> str:
        """
        Returns the name for the given cell in the TileSet.
        """
        return self._NAMEPLATE.format(self.name, cell.x, cell.y)

    def __draw(self, cell: p3d.LPoint2i) -> list:
        """
        Returns the Texture data of the given Tile as a PTAUchar.
        """
        return np.flip(
            np.flip(self._data, axis = 0)[
                (x := (self.rules.tile_size.x
                       + self.rules.tile_offset.x
                       ) * (cell.x - 1)) : x + self.rules.tile_size.x,
                (y := (self.rules.tile_size.y
                       + self.rules.tile_offset.y
                       ) * (cell.y - 1)) : y + self.rules.tile_size.y,
                ], axis = 0)

    def get(self,
            cell: p3d.LPoint2i,
            blend: typing.Optional[p3d.LVector4i] = None,
            ) -> p3d.Texture:
        """
        Returns the Texture for the given cell in the TileSet.
        """
        if (name := self._get_child_name(cell)) in self:
            return self[name]

        data = self.__draw(cell)
        if blend is not None:
            for i, row in enumerate(data):
                for j, cell in enumerate(row):
                    if tuple(cell) == blend:
                        data[i][j] = np.zeros(4)

        tex = self[name] = p3d.Texture(name)
        tex.setup_2d_texture(
            self.rules.tile_size.x,
            self.rules.tile_size.y,
            p3d.Texture.T_unsigned_byte,
            p3d.Texture.F_rgba,
            )
        tex.set_magfilter(p3d.Texture.FT_nearest)
        tex.set_ram_image(p3d.PTAUchar(data.flatten().tolist()))
        tex.compress_ram_image()
        return tex
