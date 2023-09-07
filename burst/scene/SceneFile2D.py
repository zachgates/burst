__all__ = [
    'SceneFile2D',
]


import burst

import panda3d.core as p3d

from burst.control import File
from burst.core import TileSet
from burst.scene import Scene2D


class SceneFile2D(File, extensions = ['.burst2d']):

    @staticmethod
    def read_vector(dgi):
        vec = p3d.LVector2i()
        vec.read_datagram(dgi)
        return vec

    # TEMP
    def write(self, path: str, scene: Scene2D):
        stream = p3d.OFileStream(path)
        file = p3d.DatagramOutputFile()
        file.open(stream, p3d.Filename(path))
        file.put_datagram(scene.pack())
        file.close()

    def read(self) -> Scene2D:
        stream = p3d.IFileStream(str(self.path))
        file = p3d.DatagramInputFile()
        file.open(stream, self.get_path())
        file.get_datagram(dg := p3d.Datagram())
        dgi = p3d.DatagramIterator(dg)

        scene = Scene2D(
            dgi.get_fixed_string(0xFF), # title
            self.read_vector(dgi), # resolution
            dgi.get_uint8(), # frame_rate
            )

        # path = dgi.get_fixed_string(0xFF)
        # size = self.read_vector(dgi)
        # data = dgi.get_blob32()
        #
        # rules = TileSet.Rules()
        # rules.read_datagram(dgi)
        #
        # scene.load_tilesheet(
        #     TextureFile(p3d.Filename('data/tiles/' + path + '.png')),
        #     rules,
        #     )

        for i in range(dgi.get_uint8()):
            path = dgi.get_fixed_string(0xFF).strip('\x01')
            # file = TextureFile(p3d.Filename(path))
            file = burst.store.load_file(path)
            rules = TileSet.Rules()
            rules.read_datagram(dgi)
            scene.load_tilesheet(file, rules)

        return scene
