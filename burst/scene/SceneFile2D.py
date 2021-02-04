__all__ = ['SceneFile2D']


from typing import Tuple

import panda3d.core as p3d


class SceneFile2D(burst.control.File, extensions = ['.burst2d']):

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
