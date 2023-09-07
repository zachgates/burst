__all__ = [
    'SceneRenderer2D', 'Scene2D',
]


import typing

import panda3d.core as p3d

from burst.control import VFS
from burst.core import TextureFile, Tile, TileSet
from burst.scene import SceneRendererBase


class SceneRenderer2D(SceneRendererBase):

    def pack(self):
        dg = super().pack()
        print(len(self._sheets))
        dg.add_uint8(len(self._sheets))
        for i, ts in self._sheets.items():
            path = p3d.Filename(ts.get_fullpath())
            path.make_relative_to(VFS.get_cwd())
            dg.add_fixed_string(path.to_os_specific(), 0xFF)
            # ts.size.write_datagram(dg)
            # dg.add_blob32(ts.get_ram_image().get_data())
            ts.rules.write_datagram(dg)
        return dg

    def __init__(self, title: str, resolution: tuple, frame_rate: int):
        super().__init__(title, resolution, frame_rate)

        self._sheets = {}

        self._root = base.aspect2d.attach_new_node('root')
        self._next_sort_layer = 100
        self._layers = {}

    def add_layer(self, name: str) -> p3d.NodePath:
        if name in self._layers:
            raise ValueError(f'layer exists for {name!r}')

        cbm = p3d.CullBinManager.get_global_ptr()
        cbm.add_bin(name, cbm.BT_back_to_front, self._next_sort_layer)
        self._next_sort_layer += 1

        layer = self._layers[name] = self._root.attach_new_node(name)
        layer.set_bin(name, 1)
        return layer

    def get_layer(self, name: str) -> p3d.NodePath:
        if name in self._layers:
            return self._layers[name]
        else:
            raise KeyError(f'no layer exists for {name!r}')

    def load_tilesheet(self, file: TextureFile, rules: TileSet.Rules):
        index = len(self._sheets)
        tiles = self._sheets[index] = TileSet(file.read(), rules)
        print(f'load_tilesheet({str(file.path)!r}) @ ({index})')
        return tiles

    def tiles(self, index: int):
        return self._sheets[index]


Scene2D = SceneRenderer2D
