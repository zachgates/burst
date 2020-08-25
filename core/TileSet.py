import math

from dataclasses import dataclass, field
from typing import Generator, List, Mapping, Optional, Tuple

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from .TexturePool import TexturePool
from .XYRuleset import XYRuleset


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class XYDataset(object):

    _DTYPE = p3d.LPoint2i
    _EMPTY = p3d.LVector4i.zero()

    def __init__(self, width, height, data, mode):
        self.__size = p3d.LVector2i(width, height)
        self.__mode = mode
        self._data = memoryview(data)
        self._grid = {}

    @property
    def width(self):
        return self.__size.x

    @property
    def height(self):
        return self.__size.y

    def get(self, point: _DTYPE):
        return tuple(self._grid.get(point, self._EMPTY))

    def select(self, start: [int, _DTYPE], end: [int, _DTYPE] = None):
        """
        Generate a slice of the 2D (X, Y) matrix.
        """
        try:
            # Getting a single "start" point
            if end is None:
                cell = None
                try:
                    # Get the point by index
                    cell = self[start]
                except TypeError:
                    # Get the point from the grid
                    assert isinstance(start, self._DTYPE)
                    cell = self.get(start)
                finally:
                    # Wrap the single cell
                    yield iter([cell])
            else:
                try:
                    # Get points by index
                    yield (self[n] for n in range(start, end + 1))

                except TypeError:
                    # Get points from the grid
                    assert isinstance(start, self._DTYPE)
                    assert isinstance(end, self._DTYPE)

                    # Generate [start, end] slice
                    for x in range(start.x, end.x + 1):
                        yield (self.get(self._DTYPE(x, y))
                               for y in range(start.y, end.y + 1))

        except AssertionError:
            LOG.warning(f'invalid selection: {start} -> {end}')
            return None


class PixelSet(XYDataset):

    _BLANK = p3d.LVector4i.zero()

    def __init__(self, tex: p3d.Texture, mode = 'BGRA'):
        if tex and tex.hasRamImage():
            width, height = (tex.getXSize(), tex.getYSize())
            data = tex.getRamImageAs(mode)
        else:
            width = height = 0
            data = b''

        super().__init__(width, height, data, mode)

        for offset in range(0, len(data), len(mode)):
            # Determine cell data
            color = self._data[offset : offset + len(mode)]
            index = offset // len(mode)
            point = p3d.LPoint2i(
                x = self.height - (index // self.width),
                y = index % self.width + 1)

            # Define the cell
            self._grid[point] = color


class TileSet(TexturePool):

    class Rules(XYRuleset):
        _RULES = ('tile_size', 'tile_run', 'tile_offset')

    class Tiles(XYDataset):
        pass

    def __init__(self, f_path: str, ruleset: dict):
        super().__init__()
        self._atlas = self.loadTexture(p3d.Filename(f_path))
        self._rules = self.Rules(**ruleset)
        self._pixelmat = PixelSet(self._atlas, )

        if self._atlas and self._rules:
            LOG.info(f'loaded tileset: "{f_path}"')
        else:
            LOG.warning(f'failed to load tileset: "{f_path}"')
            return

        # for row in range(self._rules.tile_run.y):
        #     self._pixelmat[row + 1] = {0: PixelSet._BLANK}
        #     for col in range(self._rules.tile_run.x):
        #         x, y = (row + 1), (col + 1)
        #         n = (row * self._rules.tile_run.x) + y
        #         self._pixelmat[x][y] = self._tilemap[n] = self.Tile(
        #             index = n,
        #             position = (x, y),
        #             size = (self._rules.tile_size.x, self._rules.tile_size.y))

        # Initialize the tile maker
        self.__tile_maker = p3d.CardMaker(f'tile-maker:{self.name}')
        self.__tile_maker.setFrameFullscreenQuad()
        self.__tiletex_nameplate = 'tex:ref:{0}:{1}'

    @property
    def name(self):
        """
        Returns the name of the Texture containing the atlas of the TileSet.
        """
        if self._atlas:
            name = self._atlas.getName()
        else:
            name = 'empty'

        return f'<{name}>'

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
    def tiles(self) -> Tuple[int, p3d.Texture]:
        """
        Returns a list of all the Tiles in the TileSet, sorted by index.
        """
        return sorted(self._tilemap.values(), key = lambda tile: tile.index)

    @property
    def count(self) -> int:
        """
        Returns the number of tiles in the TileSet. Returns -1 if the atlas
        Texture fails to load.
        """
        if self.atlas:
            return (self.rules.tile_run.x * self.rules.tile_run.y)
        else:
            return -1

    def get(self, tile_index: int) -> p3d.Texture:
        """
        Returns the n-th tile in the TileSet.
        """
        try:
            tile_index %= (self.count + 1)
        except ZeroDivisionError:
            return None

        if tile_index in self._tilemap:
            tex = self._tilemap[tile_index]
        else:
            tex = self._generate(tile_index)
            self._tilemap[tile_index] = tex

        return tex

    def make(self, tile_index: int) -> p3d.NodePath:
        tex = self.get(tile_index)
        tile = self.__tile_maker.generate()
        tile.setName(self.__tiletex_nameplate.format(tile_index, self.name))
        tileNP = aspect2d.attachNewNode(tile)
        print(tex)
        tileNP.setTexture(tex)
        return tileNP

    def __getPixelOffset(self, tile_index: int) -> Tuple[int, int]:
        """
        Returns the (x, y) pixel offset for a given tile, from the bottom
        right corner of the tileset.
        """
        x_size, y_size = self.rules.tile_size
        x_run, y_run = self.rules.tile_run
        x_offset, y_offset = self.rules.tile_offset

        row = math.ceil(tile_index / x_run) - 1
        row_offset = (y_run - (row + 1)) * (y_size + y_offset)
        row_offset *= self.atlas.getXSize()

        col = (tile_index - 1) % x_run
        col_offset = (x_size + x_offset) * col

        return (row_offset, col_offset)

    def _generate(self, tile_index: int, mode: str = 'BGRA') -> p3d.Texture:
        """
        Generate a Texture for the n-th tile in the TileSet.
        """
        image = self.atlas.getRamImageAs('BGRA')
        x_size, y_size = self.rules.tile_size
        x_run, y_run = self.rules.tile_run
        x_offset, y_offset = self.rules.tile_offset

        pixels = []
        for i in range(0, ((x_size * x_run) * (y_size * y_run) * 4), 4):
            pixel = PixelSet.Pixel()
            pixel = [image.getElement(i + j) for j in range(4)]
            pixels.append(pixel)

        for row in range(x_run):
            for col in range(y_run):
                PixelSet.Pixel(mode, tuple(data), (row + 1, col + 1))

        x_offset, y_offset = self.__getPixelOffset(tile_index)
        offset = row_offset + col_offset

        m = []
        for i in range(y_size):
            k = []
            for j in range(x_size):
                n = j + row_offset + col_offset + (self.atlas.getXSize() * i)
                k += pixels[n]
            m += k

        data = p3d.PTAUchar()
        data.setData(m)

        tex = p3d.Texture(self.__tiletex_nameplate.format(tile_index, self.name))
        tex.setup2dTexture(x_size, y_size, p3d.Texture.TUnsignedByte, p3d.Texture.FRgba)
        tex.setMagfilter(p3d.Texture.FTNearest)
        tex.setRamImage(data)
        return tex
