from panda3d import core as p3d
from direct.directnotify import DirectNotifyGlobal
from direct.stdpy.file import StreamIOWrapper


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class SceneLoaderBase(StreamIOWrapper):

    def __init__(self, f_name: p3d.Filename):
        if f_name:
            assert f_name.exists()
            self.__root = f_name
            self.__strm = p3d.IFileStream(self.path)
        else:
            self.__root = self.__strm = None

    @property
    def path(self) -> str:
        return self.__root.getFullpath()

    @property
    def _stream(self) -> p3d.istream:
        return self.__strm

    def __enter__(self):
        LOG.debug(f'loading scene: {self.path}')
        self.__root.setBinary()
        assert self.__root.openRead(self._stream)
        super().__init__(self._stream)
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
