from direct.stdpy.file import StreamIOWrapper


class InputManager(StreamIOWrapper):

    def __init__(self):
        self.__root = self.__strm = None

    @property
    def path(self) -> str:
        return self.__root.getFullpath()

    @property
    def file(self) -> burst.p3d.DatagramInputFile:
        return self.__fobj

    def __call__(self, f_name: burst.p3d.Filename):
        assert f_name.exists()
        self.__root = f_name
        self.__strm = burst.p3d.IFileStream(self.path)
        self.__fobj = burst.p3d.DatagramInputFile()
        assert self.__fobj.open(self.__strm, self.path)
        return self

    def __enter__(self):
        self.__root.setBinary()
        assert self.__root.openRead(self.__strm)
        super().__init__(self.__strm)
        assert super().readable()
        return self

    def __exit__(self, *exc) -> bool:
        # Close the file before propagating the exception.
        super().close()
        return False

    def read(self, n_bytes: int = -1) -> bytes:
        if self.tell() >= 0:
            return super().read(n_bytes)
        else:
            return b''

    def load(self):
        return NotImplemented
