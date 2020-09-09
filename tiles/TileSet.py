import math

from typing import Optional

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from ..core.PixelMatrix import PixelMatrix
from ..core.TexturePool import TexturePool

from .Tile import Tile
from .TileRules import TileRules


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileSet(TexturePool):

    def __init__(self, f_path: p3d.Filename, **rules):
        super().__init__()
        self.rules = TileRules(**rules)
        self.atlas = super().loadTexture(f_path)
        self.pixel = PixelMatrix(self.atlas)

    @property
    def name(self) -> str:
        return f"<{self.atlas.getName() if self.atlas else 'empty'}>"

    @property
    def path(self) -> str:
        return self.atlas.getFullpath()

    @property
    def size(self) -> int:
        """
        Returns the size, in pixels, of the tiles in the TileSet.
        """
        return (self.rules.tile_size.x * self.rules.tile_size.y)

    @property
    def count(self) -> int:
        """
        Returns the number of tiles in the TileSet. Returns -1 if the sheet
        Texture fails to load.
        """
        if self.atlas:
            return (self.rules.tile_run.x * self.rules.tile_run.y)
        else:
            return -1

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

        return p3d.PTAUchar(px_data)

    def makeTexture(self, index: int):
        tex = Tile(index)
        tex.setMagfilter(p3d.Texture.FTNearest)
        tex.setup2dTexture(self.rules.tile_size.x, self.rules.tile_size.y,
                           p3d.Texture.TUnsignedByte, p3d.Texture.FRgba)
        return tex

    def findTexture(self, index: int):
        return super().findTexture(Tile.getName(index))

    def findAllTextures(self) -> p3d.TextureCollection:
        return super().findAllTextures(Tile.getName('*'))

    def loadTexture(self, index: int) -> Optional[p3d.Texture]:
        """
        Returns the Texture for the n-th Tile in the TileSet.
        """
        index %= (self.count + 1)
        f_name = Tile.getName(index)
        f_path = Tile.getPath(index)

        if self.hasTexture(f_name):
            LOG.debug(f'loading tile from pool: {index}')
            return self.findTexture(index)

        if burst.cache.active:
            tile = burst.cache.lookup(f_path)
            if tile:
                LOG.debug(f'loaded tile from cache: {index} @ {f_path}')
                tile.setFullpath(f_name)
                self.addTexture(tile)
                return tile
            else:
                LOG.debug(f'tile not in cache: {index}')

        LOG.debug(f'loading tile from tilesheet: {index}')
        tile = self.makeTexture(index)
        tile.setFullpath(f_path)
        tile.setRamImage(self.__draw(index))
        tile.compressRamImage()

        if burst.cache.active:
            burst.cache.store(tile)

        self.addTexture(tile)
        return tile

    def verifyTexture(self, index: int) -> bool:
        return True
