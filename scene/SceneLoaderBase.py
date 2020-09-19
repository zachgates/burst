from panda3d import core as p3d
from direct.directnotify import DirectNotifyGlobal
from direct.stdpy.file import StreamIOWrapper


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class SceneLoaderBase(StreamIOWrapper):

    def __init__(self):
        self.__root = self.__strm = None

    @property
    def path(self) -> str:
        return self.__root.getFullpath()

    @property
    def file(self) -> p3d.DatagramInputFile:
        return self.__fobj

    def __call__(self, f_name: p3d.Filename):
        assert f_name.exists()
        self.__root = f_name
        self.__strm = p3d.IFileStream(self.path)
        self.__fobj = p3d.DatagramInputFile()
        assert self.__fobj.open(self.__strm, self.path)
        return self

    def __enter__(self):
        LOG.debug(f'loading scene: {self.path}')
        self.__root.setBinary()
        assert self.__root.openRead(self.__strm)
        super().__init__(self.__strm)
        assert super().readable()
        return self

    def __exit__(self, *exc) -> bool:
        if not exc:
            LOG.debug(f'done loading scene: {self.path}')

        # close before propagating exception
        super().close()
        return False

    def read(self, n_bytes: int = -1) -> bytes:
        if self.tell() >= 0:
            return super().read(n_bytes)
        else:
            LOG.warning('cannot read past EOF')
            return b''

    def load(self):
        return NotImplemented
