import math


class TileSet(dict):

    def __init__(self, f_path: str, **rules):
        super().__init__()
        self.rules = burst.tile.AtlasRules(**rules)
        if f_path:
            self.atlas = loader.loadTexture(f_path)
            self.pixel = burst.core.PixelMatrix(self.atlas)
        else:
            self.atlas = self.pixel = None

    @property
    def name(self) -> str:
        return f"<{self.atlas.getName() if self.atlas else 'empty'}>"

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
            off = burst.p3d.LVector2i(
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
                off.y += (self.rules.tile_run.x * self.rules.tile_size.x) \
                         + (self.rules.tile_run.x - 1) \
                         * self.rules.tile_offset.x
                px_rows.append([self.pixel.get(index = offset + col)
                                for col in range(self.rules.tile_size.x)])

        px_data = bytearray()
        for row in px_rows[::-1]:
            for cell in row:
                px_data += bytes(cell.getXyz())
                px_data += bytes([cell.getW()])

        return burst.p3d.PTAUchar(px_data)

    def get(self, index: int) -> burst.p3d.Texture:
        """
        Returns the Texture for the n-th Tile in the TileSet.
        """
        index %= (self.count + 1)
        name = burst.tile.Tile.getName(self, index)

        if name in self:
            tile = self[name]
        else:
            tile = self[name] = burst.tile.Tile(name, index)
            tile.setup2dTexture(
                self.rules.tile_size.x,
                self.rules.tile_size.y,
                burst.p3d.Texture.TUnsignedByte,
                burst.p3d.Texture.FRgba)
            tile.setMagfilter(burst.p3d.Texture.FTNearest)
            tile.setRamImage(self.__draw(index))
            tile.compressRamImage()

        return tile
