__all__ = [
    'SceneFile2D',
]


import panda3d.core as p3d

from burst.control import File
from burst.core import TileSet
from burst.scene import Scene2D


class SceneFile2D(File, extensions = ['.burst2d']):

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

        def read_vector(dgi):
            vec = p3d.LVector2i()
            vec.read_datagram(dgi)
            return vec

        return Scene2D(
            dgi.get_fixed_string(0xFF),
            read_vector(dgi),
            TileSet(
                dgi.get_fixed_string(0xFF),
                read_vector(dgi),
                dgi.get_blob32(),
                **{
                    'tile_size': read_vector(dgi),
                    'tile_run': read_vector(dgi),
                    'tile_offset': read_vector(dgi),
                }))
