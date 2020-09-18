from typing import Generator

from panda3d import core as p3d

from . import SceneLoaderBase
from . import Scene2D


class SceneLoader2D(SceneLoaderBase):

    def __init__(self, f_name: p3d.Filename):
        super().__init__(f_name)
        self.__fobj = p3d.DatagramInputFile()
        assert self.__fobj.open(self._stream, self.path)

    def _unpack(self) -> Generator:
        dg = p3d.Datagram()
        self.__fobj.getDatagram(dg)
        dgi = p3d.DatagramIterator(dg)

        yield from (
            # scene name
            dgi.getFixedString(0xff),
            # scene size
            self._unpack_rule(dgi),
            # atlas name
            dgi.getFixedString(0xff),
            # atlas ram image
            dgi.getBlob32(),
            # atlas size
            self._unpack_rule(dgi),
            # atlas rules
            {
                'tile_size': self._unpack_rule(dgi),
                'tile_run': self._unpack_rule(dgi),
                'tile_offset': self._unpack_rule(dgi),
            },
        )

    def _unpack_rule(self, dgi):
        return (dgi.getUint16(), dgi.getUint16())

    def read(self) -> Scene2D:
        data = self._unpack()
        return Scene2D(*data)
