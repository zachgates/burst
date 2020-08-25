from dataclasses import dataclass
from typing import Mapping, Tuple

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject

from .Tile import TileTexture


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)
OPT = ('size', 'run', 'offset')


class SheetTexture(p3d.Texture):

    def __new__(cls, f_path, f_opts):
        # texturePool.cxx L:233
        f_path = p3d.Filename(f_path)
        tex = burst.data.loader.loadTexture(f_path)
        if tex:
            LOG.info(f'loaded: "{f_path}"; from cache: "{tex.getFullpath()}"')
        else:
            LOG.warning(f'failed to load: "{f_path}"')
            tex = p3d.Texture()
        return tex

    def __init__(self, *args, **kwargs):
        print(args, kwargs)

    @property
    def size(self):
        return (self._tex.getXSize(), self._tex.getYSize())


class TileSheet(DirectObject):

    @dataclass
    class Properties:
        texture: p3d.Texture
        size: Tuple[int, int]
        options: Mapping[str, Tuple]

        def __post_init__(self):
            self.__image = self.texture.getRamImage()
            opts = dict((name, (0, 0)) for name in OPT)
            try:
                if isinstance(self.options, dict):
                    for name in self.options:
                        if name in opts:
                            opts[name] = self.options[name]
                else:
                    for name, opt in zip(opts, self.options):
                        try:
                            opt_x, opt_y = opt
                            opts[name] = (opt_x, opt_y)
                        except (TypeError, ValueError):
                            LOG.warning(f'bad value for option "{name}": {opt}')
                        else:
                            LOG.debug(f'set option "{name}": {opt}')
            except TypeError:
                LOG.warning(f'bad options: {self.options}')
            finally:
                self.options = opts

        @property
        def _bytes(self):
            return self.__image.getData()

    def __init__(self):
        super().__init__()
        self._tex = None
        self.__tile_maker = p3d.CardMaker('tile-maker')
        self.__tile_maker.setFrameFullscreenQuad()
        self.__tile_cache = {}
        self.__tiletex_nameplate = 'tex:ref:{0}:{1}'

    @property
    def name(self):
        return self._tex.getName()

    @property
    def texture(self):
        return self._tex

    @property
    def tilesize(self):
        return self._cell_size

    def load(self, f_path, f_opts):
        if self.texture:
            LOG.warning(f'already loaded: {self.name}')
        else:
            self._cell_size = f_opts[0]
            f_path = p3d.Filename(f_path)
            self._tex = burst.data.loader.loadTexture(f_path)

    def hasTile(self, ref):
        return (ref in self.__tile_cache)

    def getTile(self, ref):
        if self.hasTile(ref):
            return self.__tile_cache[ref]
        else:
            # tile = self.__generateTile(ref)
            # self.__tile_cache[ref] = tile
            # return tile
            pass

    def __generateTile(self, ref):
        tex = burst.data.loader.loadTexture(p3d.Filename('fake.png'))
        tile = self.__tile_maker.generate()
        tile.setName(self.__tiletex_nameplate.format(ref, self.name))
        tileNP = aspect2d.attachNewNode(tile)
        tileNP.setTexture(tex)
        return tileNP

    def select_tile(self, ref):
        width, height = self.data.options['size']
        # Unpack options
        t_size_x, t_size_y = self.data.options.get('size')
        t_run_x, t_run_y = self.data.options.get('run')
        t_offset_x, t_offset_y = self.data.options.get('offset')
        # Select pixels
        offset_x = (col * height) * (t_size_x + t_offset_x)
        offset_y = (t_run_y - (row + 1)) * (t_size_y + t_offset_y)

        # width * height * 4
        offset = 0
        row = (ref - 1) // t_run_x
        # row_offset = (row * t_size_x) + (row * t_offset_x)
        # row_rng = range(row_offset, row_offset + t_size_x)
        # col = (ref - 1) % t_run_y
        # col_offset = (col * t_size_y) + (col * t_offset_y)
        # col_rng = range(col_offset, col_offset + t_size_y)
        # return [self.data.image[col_rng * 4] for i in row_rng]

        # Texture format is BGRA!
        # tex.setRamImage(data)
