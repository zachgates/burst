from typing import Generator

from panda3d import core as p3d

from . import SceneLoaderBase
from . import SceneRenderer2D


class SceneLoader2D(SceneLoaderBase):

    def _unpack(self) -> Generator:
        dg = p3d.Datagram()
        self.file.getDatagram(dg)
        dgi = p3d.DatagramIterator(dg)

        yield from (
            # scene name
            dgi.getFixedString(0xff),
            # scene resolution
            self._unpackRule(dgi),
            # atlas name
            dgi.getFixedString(0xff),
            # atlas ram image
            dgi.getBlob32(),
            # atlas size
            self._unpackRule(dgi),
            # atlas rules
            {
                'tile_size': self._unpackRule(dgi),
                'tile_run': self._unpackRule(dgi),
                'tile_offset': self._unpackRule(dgi),
            },
        )

    def _unpackRule(self, dgi) -> tuple:
        return (dgi.getUint16(), dgi.getUint16())

    def read(self):
        data = self._unpack()
        return SceneRenderer2D(*data)
