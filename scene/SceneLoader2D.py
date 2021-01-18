class SceneLoader2D(burst.core.InputFileManager):

    def _unpack(self) -> tuple:
        dg = burst.p3d.Datagram()
        self.file.get_datagram(dg)
        dgi = burst.p3d.DatagramIterator(dg)
        return (
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

    def _unpack_rule(self, dgi) -> tuple:
        return (dgi.get_uint16(), dgi.get_uint16())

    def read(self):
        data = self._unpack()
        return burst.scene.Scene2D(*data)
