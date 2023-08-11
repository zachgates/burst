__all__ = [
    'SceneFile2D',
]


import panda3d.core as p3d

from burst.control import File
from burst.scene import Scene2D


class SceneFile2D(File, extensions = ['.burst2d']):

    @staticmethod
    def _unpack_rule(dgi) -> tuple[int, int]:
        return (dgi.get_uint16(), dgi.get_uint16())

    def write(self, path: str, scene: Scene2D):
        dg = p3d.Datagram()
        dg.add_fixed_string('new scene', 0xff)
        dg.add_uint16(512)
        dg.add_uint16(512)
        dg.add_fixed_string(scene.tiles.atlas.get_name(), 0xff)
        dg.add_blob32(scene.tiles.pixel.data.tobytes())
        dg.add_uint16(scene.tiles.pixel.width)
        dg.add_uint16(scene.tiles.pixel.height)
        dg.add_uint16(scene.tiles.rules.tile_size.x)
        dg.add_uint16(scene.tiles.rules.tile_size.y)
        dg.add_uint16(scene.tiles.rules.tile_run.x)
        dg.add_uint16(scene.tiles.rules.tile_run.y)
        dg.add_uint16(scene.tiles.rules.tile_offset.x)
        dg.add_uint16(scene.tiles.rules.tile_offset.y)

        stream = p3d.OFileStream(path)
        file = p3d.DatagramOutputFile()
        file.open(stream, p3d.Filename(path))
        file.put_datagram(dg)
        file.close()

    def read(self):
        stream = p3d.IFileStream(str(self.path))
        file = p3d.DatagramInputFile()
        file.open(stream, self.get_path())
        file.get_datagram(dg := p3d.Datagram())
        dgi = p3d.DatagramIterator(dg)

        return Scene2D(
            # scene name
            dgi.get_fixed_string(0xff),
            # scene resolution
            self._unpack_rule(dgi),
            # atlas name
            dgi.get_fixed_string(0xff),
            # atlas ram image
            dgi.get_blob32(),
            # atlas size
            self._unpack_rule(dgi),
            # atlas rules
            {
                'tile_size': self._unpack_rule(dgi),
                'tile_run': self._unpack_rule(dgi),
                'tile_offset': self._unpack_rule(dgi),
            },
        )
