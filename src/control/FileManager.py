from direct.showbase.DirectObject import DirectObject

from ..base import File, FileError


class FileManager(DirectObject):

    _fext = None

    def load(self, fpath, silent=False, recursive=False):
        fobj = vfs.getFile(fpath)
        try:
            if fobj and fobj.isRegularFile():
                return self.loadFile(fobj, silent)
            elif fobj and fobj.isDirectory():
                return self.loadDirectory(fobj, silent, recursive)
            else:
                return None
        except AttributeError as e:
            if not silent:
                raise e
            else:
                return None

    def loadFile(self, fobj, silent=False):
        try:
            ftype = File.find_class_by_fext(self._fext)
            return ftype(fobj.getFilename())
        except FileError as e:
            if not silent:
                raise e
            else:
                return None

    def loadDirectory(self, fobj, silent=False, recursive=False):
        for virtualFile in vfs.scanDirectory(fobj.getFilename()):
            if virtualFile.isDirectory() and not recursive:
                continue
            elif virtualFile.isDirectory():
                for file_ in self.loadDirectory(fobj, silent, recursive):
                    yield file_
            elif virtualFile.isRegularFile():
                yield self.loadFile(virtualFile, silent)
            else:
                yield None
