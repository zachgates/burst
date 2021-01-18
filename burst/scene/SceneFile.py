__all__ = ['SceneFile']


from typing import Tuple

from panda3d import core as p3d


class SceneFile(burst.control.File, extensions = ['.burst']):

    @staticmethod
    def _unpack_rule(dgi) -> Tuple[int, int]:
        return (dgi.get_uint16(), dgi.get_uint16())

    def read(self):
        stream = p3d.IFileStream(str(self.path))
        file = p3d.DatagramInputFile()
        file.open(stream, self.get_path())

        dg = p3d.Datagram()
        file.get_datagram(dg)
        dgi = p3d.DatagramIterator(dg)

        return burst.scene.Scene2D(
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
