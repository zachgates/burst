from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class TileCache(object):

    _EXT = 'tile'
    _IDX = 'index_name.txt'

    def __init__(self, sheet_path):
        self.__idx = bytes.fromhex(self.hashFilename(sheet_path))
        # Throws a PRC warning here because model-cache-dir is technically
        # a ConfigVariableSearchPath. Sacrifice to get the path as a Filename.
        self._root = p3d.ConfigVariableFilename('model-cache-dir').getValue()
        self._active = False
        if p3d.ConfigVariableBool('model-cache-tiles').getValue():
            if self.readIndex():
                self._active = True

    @property
    def active(self):
        return self._active

    def hashFilename(self, f_name: p3d.Filename) -> p3d.Filename:
        hv = p3d.HashVal()
        hv.hashString(f_name.getFullpath())
        return hv.asHex()

    def readIndex(self) -> bool:
        f_path = p3d.Filename(self._root, self._IDX)
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

        return self.rebuildIndex()

    def rebuildIndex(self):
        if self._root.exists():
            LOG.debug(f'deleting old cache @ {self._root}')
            for f_name in self._root.scanDirectory():
                f_path = p3d.Filename(f_name)
                f_path.unlink()
        else:
            self._root.mkdir()

        LOG.debug(f'rebuilding cache @ {self._root}')
        f_path = p3d.Filename(self._root, self._IDX)
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

    def store(self, tex: p3d.Texture):
        f_name = p3d.Filename(self.hashFilename(tex.getFullpath()))
        f_name.setExtension(self._EXT)
        f_path = p3d.Filename(self._root, f_name)
        f_path.setBinary()

        if not f_path.exists():
            LOG.debug(f'declaring cache file @ {f_path} for {tex}')
            stream = p3d.OFileStream()
            if f_path.openWrite(stream, True):
                buffer = p3d.DatagramBuffer()
                writer = p3d.BamWriter()
                writer.setTarget(buffer)
                writer.setFileTextureMode(p3d.BamWriter.BTMRawdata)
                writer.writeObject(tex)
                writer.flush()
                assert writer.hasObject(tex)
                stream.write(buffer.data)
                stream.close()
                assert stream.good()
                return True
            else:
                LOG.warning(f'could not write cache file @ {f_path}')
        else:
            LOG.debug(f'cache file exists @ {f_path}')

        return False

    def lookup(self, f_name: p3d.Filename) -> p3d.BamCacheRecord:
        f_path = p3d.Filename(self._root, self.hashFilename(f_name))
        f_path.setExtension(self._EXT)

        if f_path.exists():
            din = p3d.DatagramInputFile()
            if din.open(f_path):
                LOG.debug(f'reading cache file @ {f_path}')
                reader = p3d.BamReader(din)
                assert reader.init()
                tex = reader.readObject()
                if tex:
                    if reader.resolve():
                        return tex
                    else:
                        LOG.warning(f'unable to fully resolve tile @ {f_path}')
                else:
                    LOG.warning(f'invalid cache file @ {f_path}')
            else:
                LOG.warning(f'could not read existing cache file @ {f_path}')

            # Get rid of the corrupt cache file
            f_path.unlink()
        else:
            LOG.debug(f'cache file does not exist @ {f_path}');

        return None
