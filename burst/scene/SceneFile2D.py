__all__ = [
    'SceneFile2D',
]


import panda3d.core as p3d

from burst.control import File
from burst.core import TileSet
from burst.scene import Scene2D


class SceneFile2D(File, extensions = ['.burst2d']):

    @staticmethod
    def _unpack_vec2d(dgi: p3d.DatagramIterator) -> p3d.LVector2i:
        return p3d.LVector2i(dgi.get_uint16(), dgi.get_uint16())

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

        return Scene2D(
            dgi.get_fixed_string(0xFF),
            self._unpack_vec2d(dgi),
            TileSet(
                dgi.get_fixed_string(0xFF),
                self._unpack_vec2d(dgi),
                dgi.get_blob32(),
                **{
                    'tile_size': self._unpack_vec2d(dgi),
                    'tile_run': self._unpack_vec2d(dgi),
                    'tile_offset': self._unpack_vec2d(dgi),
                }))
