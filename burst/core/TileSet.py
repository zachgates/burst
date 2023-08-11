__all__ = [
    'Tile', 'TileSet',
]


import burst
import dataclasses
import math

import panda3d.core as p3d

from burst.core import PixelMatrix, RuleBase, Rule2D


class Tile(p3d.Texture):

    def __init__(self, name: str, index: int = 0):
        super().__init__(name)
        self.__idx = index

    def __hash__(self):
        return self.name

    @property
    def index(self):
        return self.__idx


class TileSet(dict):

    _NAMEPLATE = 'tex:{0}:ref:{1}'

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
            self.pixel = PixelMatrix(self.atlas)
        else:
            self.atlas = self.pixel = None

    @property
    def name(self) -> str:
        return f"<{self.atlas.get_name() if self.atlas else 'empty'}>"

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

    def __draw(self, index: int) -> bytearray:
        """
        Returns the Texture data of the Tile at index as a bytearray.
        """
        px_rows = []
        if index:
            row = math.ceil(index / self.rules.tile_run.y)
            col = ((index - 1) % self.rules.tile_run.x) + 1
            off = p3d.LVector2i(
                x = (row - 1) \
                    * (self.size \
                       * self.rules.tile_run.y \
                       + (self.rules.tile_run.x - 1) \
                       * self.rules.tile_size.y \
                       * self.rules.tile_offset.x \
                       + self.rules.tile_offset.y \
                       * self.pixel.width),
                y = (col - 1) \
                    * (self.rules.tile_size.x \
                       + self.rules.tile_offset.x))

            for row in range(self.rules.tile_size.y):
                offset = (off.x + off.y + 1)
                off.y += (
                    (self.rules.tile_run.x * self.rules.tile_size.x)
                    + (self.rules.tile_run.x - 1)
                    * self.rules.tile_offset.x
                    )
                px_rows.append([self.pixel.get(index = offset + col)
                                for col in range(self.rules.tile_size.x)])

        px_data = bytearray()
        for row in px_rows[::-1]:
            for cell in row:
                px_data += bytes([ # BGRA
                    cell.get_x(),
                    cell.get_y(),
                    cell.get_z(),
                    cell.get_w(),
                    ])

        return p3d.PTAUchar(px_data)

    def get_child_name(self, index: int) -> str:
        return self._NAMEPLATE.format(self.name, index)

    def get(self, index: int) -> p3d.Texture:
        """
        Returns the Texture for the n-th Tile in the TileSet.
        """
        index %= (self.count + 1)
        name = self.get_child_name(index)

        if name in self:
            tile = self[name]
        else:
            tile = self[name] = Tile(name, index)
            tile.setup_2d_texture(
                self.rules.tile_size.x,
                self.rules.tile_size.y,
                p3d.Texture.T_unsigned_byte,
                p3d.Texture.F_rgba,
                )
            tile.set_magfilter(p3d.Texture.FT_nearest)
            tile.set_ram_image(self.__draw(index))
            tile.compress_ram_image()

        return tile
