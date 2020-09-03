import math
import uuid

from dataclasses import dataclass, field
from typing import Generator, List, Mapping, Optional, Tuple

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from .PixelMatrix import PixelMatrix
from .TileCache import TileCache
from .XYRuleset import XYRuleset
from ..tools.TexturePool import TexturePool


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileSet(TexturePool):

    class Rules(XYRuleset):
        _AFFIX = 'tile'
        _RULES = ('size', 'run', 'offset')

    def __init__(self, f_path: p3d.Filename, **rules):
        super().__init__()
        self._rules = self.Rules(**rules)
        self._sheet = super().loadTexture(f_path)
        self._pxmat = PixelMatrix(self._sheet)
        self.__name = 'tex:{0}:ref:{1}'

    @property
    def name(self) -> str:
        """
        Returns the name of the Texture containing the TileSet.
        """
        return f"<{self._sheet.getName() if self._sheet else 'empty'}>"

    @property
    def path(self) -> str:
        hv = p3d.HashVal()
        hv.hashFile(self._sheet.getFullpath())
        return hv.asHex()

    @property
    def count(self) -> int:
        """
        Returns the number of tiles in the TileSet. Returns -1 if the sheet
        Texture fails to load.
        """
        if self._sheet:
            return (self._rules.tile_run.x * self._rules.tile_run.y)
        else:
            return -1

    @property
    def page_size(self) -> int:
        """
        Returns the size, in pixels, of the tiles in the TileSet.
        """
        return (self._rules.tile_size.x * self._rules.tile_size.y)

    def _getTilePath(self, index: int) -> str:
        base = uuid.UUID(self.path)
        path = uuid.uuid3(base, hex(index))
        fake = p3d.Filename(self._sheet.getFullpath())
        return p3d.Filename(fake.getFullpathWoExtension(),
                            p3d.Filename(f'{path.hex}.tile'))

    def __getTileData(self, index: int) -> bytearray:
        """
        Returns the Texture data of the Tile at index as a bytearray.
        """
        px_rows = []
        if index:
            row = math.ceil(index / self._rules.tile_run.y)
            col = ((index - 1) % self._rules.tile_run.x) + 1
            off = p3d.LVector2i(
                x = (row - 1) \
                    * (self.page_size \
                       * self._rules.tile_run.y \
                       + (self._rules.tile_run.x - 1) \
                       * self._rules.tile_size.y \
                       * self._rules.tile_offset.x \
                       + self._rules.tile_offset.y \
                       * self._pxmat.width),
                y = (col - 1) \
                    * (self._rules.tile_size.x \
                       + self._rules.tile_offset.x))

            for row in range(self._rules.tile_size.y):
                offset = (off.x + off.y + 1)
                off.y += (self._rules.tile_run.x * self._rules.tile_size.x) \
                         + (self._rules.tile_run.x - 1) \
                         * self._rules.tile_offset.x
                px_rows.append([self._pxmat.get(index = offset + col)
                                for col in range(self._rules.tile_size.x)])

        px_data = bytearray()
        for row in px_rows[::-1]:
            for cell in row:
                px_data += bytes(cell.getXyz())
                px_data += bytes([cell.getW()])

        return p3d.PTAUchar(px_data)

    def makeTexture(self, index: int):
        tex = p3d.Texture(self.__name.format(self.name, index))
        tex.setMagfilter(p3d.Texture.FTNearest)
        tex.setup2dTexture(self._rules.tile_size.x, self._rules.tile_size.y,
                           p3d.Texture.TUnsignedByte, p3d.Texture.FRgba)
        return tex

    def findTexture(self, index: int):
        return super().findTexture(self.__name.format(self.name, index))

    def findAllTextures(self) -> p3d.TextureCollection:
        return super().findAllTextures(self.__name.format(self.name, '*'))

    def loadTexture(self, index: int) -> Optional[p3d.Texture]:
        """
        Returns the Texture for the n-th Tile in the TileSet.
        """
        index %= (self.count + 1)
        f_name = self.__name.format(self.name, index)

        if self.hasTexture(f_name):
            LOG.debug(f'loading tile from pool: {index}')
            return self.findTexture(index)

        if burst.cache.active:
            cache_path = self._getTilePath(index)
            cache_tile = burst.cache.lookup(cache_path)
            if cache_tile:
                LOG.debug(f'loaded tile from cache: {index} @ {cache_path}')
                cache_tile.setFullpath(f_name)
                self.addTexture(cache_tile)
                return cache_tile
            else:
                LOG.debug(f'tile not in cache: {index}')

        LOG.debug(f'loading tile from tilesheet: {index}')
        tex = self.makeTexture(index)
        tex.setFullpath(self._getTilePath(index))
        tex.setRamImage(self.__getTileData(index))
        tex.compressRamImage()

        self.addTexture(tex)
        if burst.cache.active:
            burst.cache.store(tex)

        return tex

    def verifyTexture(self, index: int) -> bool:
        return True
