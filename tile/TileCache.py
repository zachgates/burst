from typing import Optional

from panda3d import core as p3d
from direct.directnotify import DirectNotifyGlobal

from .Tile import Tile


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileCache(object):

    _EXT = 'tile'
    _IDX = 'index_name.txt'
    _BAM_HEAD = 'pbj\0\n\r'

    @staticmethod
    def hashFilename(f_name: p3d.Filename) -> str:
        """
        Returns the hashed cache basename of the supplied Filename.
        """
        hv = p3d.HashVal()
        hv.hashString(f_name.getFullpath())
        return hv.asHex()

    @classmethod
    def _read(cls, f_path: p3d.Filename) -> p3d.Texture:
        """
        Low-level read Texture from supplied stream at f_path.
        """
        stream = p3d.IFileStream()
        assert f_path.openRead(stream)

        din = p3d.DatagramInputFile()
        assert din.open(stream, f_path)
        header = stream.read(6)
        assert (header == cls._BAM_HEAD.encode())

        reader = p3d.BamReader(din)
        assert reader.init()
        tex = reader.readObject()
        assert reader.resolve()

        stream.close()
        return tex

    @classmethod
    def _write(cls, f_path: p3d.Filename, tile: p3d.Texture) -> None:
        """
        Low-level write Tile to supplied stream at f_path.
        """
        stream = p3d.OFileStream()
        assert f_path.openWrite(stream, True)

        dout = p3d.DatagramOutputFile()
        assert dout.open(stream, f_path)
        assert dout.writeHeader(cls._BAM_HEAD)

        writer = p3d.BamWriter(dout)
        assert writer.init()
        writer.setFileTextureMode(p3d.BamWriter.BTMRawdata)
        assert writer.writeObject(tile)
        writer.flush()

        stream.close()
        assert stream.good()

    def __init__(self, atlas_path):
        self.__idx = bytes.fromhex(self.hashFilename(atlas_path))

        search = p3d.ConfigVariableSearchPath('model-cache-dir')
        self.__root = search.getDirectories()[0]

        self.__active = False
        if p3d.ConfigVariableBool('model-cache-tiles').getValue():
            if self._readIndex():
                self.__active = True

    @property
    def root(self) -> str:
        return self.__root

    @property
    def active(self) -> bool:
        return self.__active

    def _readIndex(self) -> bool:
        """
        Tries to resolve an existing cache directory and index.
        """
        f_path = p3d.Filename(self.root, self._IDX)
        f_path.setBinary()

        if f_path.exists():
            LOG.debug(f'reading cache index @ {f_path}')
            stream = p3d.IFileStream()
            if f_path.openRead(stream):
                if stream.readall() == self.__idx:
                    return True
                else:
                    LOG.debug(f'cache index is stale @ {f_path}')
            else:
                LOG.warning(f'could not read cache index @ {f_path}')
        else:
            LOG.debug(f'no cache index present @ {f_path}')

        return self._rebuildIndex()

    def _rebuildIndex(self) -> bool:
        """
        Rebuilds the cache directory and index.
        """
        if self.root.exists():
            LOG.debug(f'deleting old cache @ {self.root}')
            for f_name in self.root.scanDirectory():
                f_path = p3d.Filename(f_name)
                f_path.unlink()
        else:
            self.root.mkdir()

        LOG.debug(f'rebuilding cache @ {self.root}')
        f_path = p3d.Filename(self.root, self._IDX)
        f_path.setBinary()

        stream = p3d.OFileStream()
        if f_path.openWrite(stream, True):
            stream.write(self.__idx)
            stream.close()
            assert stream.good()
            return True
        else:
            LOG.error(f'could not write cache index @ {f_path}')
            return False

    def _getCachePath(self, f_name: p3d.Filename) -> str:
        """
        Returns the path to which the given Filename will be written, within
        the cache directory.
        """
        f_path = p3d.Filename(self.root, self.hashFilename(f_name))
        f_path.setExtension(self._EXT)
        f_path.setBinary()
        return f_path

    def lookup(self, f_name: p3d.Filename) -> Optional[p3d.Texture]:
        """
        Searches for an existing cache Tile for the supplied Filename.
        """
        f_path = self._getCachePath(f_name)
        if f_path.exists():
            try:
                LOG.debug(f'reading cache tile @ {f_path}')
                return self._read(f_path)
            except AssertionError:
                LOG.warning(f'could not read cache tile @ {f_path}')
                f_path.unlink()
        else:
            LOG.debug(f'cache tile does not exist @ {f_path}')

    def store(self, tile: Tile) -> Optional[bool]:
        """
        Tries to store the supplied Tile in the cache.
        """
        f_path = self._getCachePath(tile.getFullpath())
        if not f_path.exists():
            try:
                LOG.debug(f'declaring cache tile @ {f_path} for {tile}')
                self._write(f_path, tile)
                return True
            except AssertionError:
                LOG.warning(f'could not write cache tile @ {f_path}')
                f_path.unlink()
                return False
        else:
            LOG.debug(f'cache tile exists @ {f_path}')
            return None
