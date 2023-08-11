__all__ = [
    'TileSet',
]


import burst
import dataclasses
import math
import numpy as np

import panda3d.core as p3d

from burst.core import RuleBase, Rule2D


class TileSet(dict):

    _NAMEPLATE = '{0}_{1}_{2}'

    @dataclasses.dataclass(init = False)
    class Rules(RuleBase):
        """
        Three rules defining the parameters of a TileSet.
        """
        tile_size: Rule2D = None
        tile_run: Rule2D = None
        tile_offset: Rule2D = None

    def __init__(self, path: str, **rules):
        super().__init__()
        self.rules = self.Rules(**rules)

        if path:
            self.atlas = base.loader.load_texture(path)
            data = self.atlas.get_ram_image_as('BGRA')
        else:
            self.atlas = None
            data = bytes()

        if self.atlas and self.atlas.has_ram_image():
            width, height = (self.atlas.get_x_size(), self.atlas.get_y_size())
        else:
            width = height = 0

        self.__size = Rule2D(width, height)
        self.__data = np.flip(
            np.reshape(data, (height, width, 4)),
            axis = 0,
            )

    @property
    def width(self) -> int:
        return self.__size.x

    @property
    def height(self) -> int:
        return self.__size.y

    @property
    def data(self) -> np.ndarray:
        return self.__data

    @property
    def name(self) -> str:
        """
        Returns the name of the TileSet.
        """
        return f"{self.atlas.get_name() if self.atlas else 'empty'}"

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

    def __draw(self, cell: p3d.LPoint2i):
        """
        Returns the Texture data of the given Tile as a PTAUchar.
        """
        return p3d.PTAUchar(
            np.flip(
                self.data[
                    (x := (self.rules.tile_size.x
                           + self.rules.tile_offset.x
                           ) * (cell.x - 1)) : x + self.rules.tile_size.x,
                    (y := (self.rules.tile_size.y
                           + self.rules.tile_offset.y
                           ) * (cell.y - 1)) : y + self.rules.tile_size.y,
                    ], axis = 0).flatten())

    def get_child_name(self, cell: p3d.LPoint2i) -> str:
        """
        Returns the name for the given cell in the TileSet.
        """
        return self._NAMEPLATE.format(self.name, cell.x, cell.y)

    def get(self, cell: p3d.LPoint2i) -> p3d.Texture:
        """
        Returns the Texture for the given cell in the TileSet.
        """
        if (name := self.get_child_name(cell)) in self:
            tile = self[name]
        else:
            tile = self[name] = p3d.Texture(name)
            tile.setup_2d_texture(
                self.rules.tile_size.x,
                self.rules.tile_size.y,
                p3d.Texture.T_unsigned_byte,
                p3d.Texture.F_rgba,
                )
            tile.set_magfilter(p3d.Texture.FT_nearest)
            tile.set_ram_image(self.__draw(cell))
            tile.compress_ram_image()

        return tile
