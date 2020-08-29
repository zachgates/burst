import math

from dataclasses import dataclass, field
from typing import Generator, List, Mapping, Optional, Tuple

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from .PixelMatrix import PixelMatrix
from .XYRuleset import XYRuleset
from ..tools.TexturePool import TexturePool


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileSet(TexturePool):

    class Rules(XYRuleset):
        _RULES = ('tile_size', 'tile_run', 'tile_offset')

    def __init__(self, f_path: str, **rules):
        super().__init__()
        self._atlas = super().loadTexture(p3d.Filename(f_path))
        self._rules = self.Rules(**{f'tile_{k}': v for k, v in rules.items()})
        self._pixelMat = PixelMatrix(self._atlas)
        self.__nameplate = 'tex:{0}:ref:{1}'

        if self._atlas and self._rules:
            LOG.info(f'loaded tileset: "{f_path}"')
        else:
            LOG.warning(f'failed to load tileset: "{f_path}"')
            return

    @property
    def name(self):
        """
        Returns the name of the Texture containing the atlas of the TileSet.
        """
        return f"<{self.atlas.getName() if self.atlas else 'empty'}>"

    @property
    def atlas(self) -> Optional[p3d.Texture]:
        """
        Returns the Texture containing the atlas image of the TileSet.
        """
        return self._atlas

    @property
    def rules(self) -> XYRuleset:
        """
        Returns the XYRuleset of the TileSet.
        """
        return self._rules

    @property
    def count(self) -> int:
        """
        Returns the number of tiles in the TileSet. Returns -1 if the atlas
        Texture fails to load.
        """
        if self._atlas:
            return (self.rules.tile_run.x * self.rules.tile_run.y)
        else:
            return -1

    @property
    def tile_size(self) -> int:
        """
        Returns the size, in pixels, of the tiles in the TileSet.
        """
        return (self.rules.tile_size.x * self.rules.tile_size.y)

    def __calcPixelData(self, index: int) -> bytearray:
        """
        Returns the Texture data of the Tile at index as a bytearray.
        """
        cells = []

        if index:
            row = math.ceil(index / self.rules.tile_run.y)
            col = ((index - 1) % self.rules.tile_run.x) + 1
            off = p3d.LVector2i(
                x = (row - 1) * self.rules.tile_run.y * self.tile_size,
                y = (col - 1) * self.rules.tile_size.x)

            for row in range(self.rules.tile_size.y):
                offset = (off.x + off.y + 1)
                off.y += (self.rules.tile_run.x * self.rules.tile_size.x)
                cells.insert(0, [self._pixelMat.get(index = offset + col)
                                 for col in range(self.rules.tile_size.x)])

        px_data = bytearray()
        for row in cells:
            for cell in row:
                px_data += bytes(cell.getXyz())
                px_data += bytes([cell.getW()])

        return px_data

    def loadTexture(self,
                    index: int,  mode: str = 'BGRA') -> Optional[p3d.Texture]:
        """
        Returns the Texture for the n-th Tile in the TileSet.
        """
        index %= (self.count + 1)
        name = self.__nameplate.format(self.name, index)

        if self.hasTexture(name):
            return self.findTexture(name)
        else:
            data = p3d.PTAUchar()
            data.setData(self.__calcPixelData(index))
            tex = p3d.Texture(name)
            tex.setup2dTexture(
                *self.rules.tile_size,
                p3d.Texture.TUnsignedByte,
                p3d.Texture.FRgba)
            tex.setMagfilter(p3d.Texture.FTNearest)
            tex.setRamImage(data)
            tex.setFullpath(tex.getName())
            self.addTexture(tex)
            return tex
