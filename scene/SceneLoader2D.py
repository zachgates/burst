class SceneLoader2D(burst.core.InputFileManager):

    def _unpack(self) -> tuple:
        dg = burst.p3d.Datagram()
        self.file.getDatagram(dg)
        dgi = burst.p3d.DatagramIterator(dg)
        return (
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
        return burst.scene.SceneRenderer2D(*data)
