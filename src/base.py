import re


class FileError(IOError):

    def __init__(self, msg):
        IOError.__init__(self)
        self._msg = msg

    def __str__(self):
        return self._msg


class File(object):

    _fext = '.*'

    @classmethod
    def check_fext(cls, fext):
        if fext:
            return bool(re.match('(?:%s)\Z' % cls._fext, fext))
        else:
            return False

    @classmethod
    def find_class_by_fext(cls, fext):
        
        for type_ in type.__subclasses__(cls):
            if type_.check_fext(fext):
                return type_
        else:
            return cls

    def __init__(self, pandaFilename, ignoreExt=False):
        object.__init__(self)

        self.__fpath = str(pandaFilename)
        self.__fname = str(pandaFilename.getBasenameWoExtension())
        self.__fext = str(pandaFilename.getExtension())
        self.__content = None

        if not ignoreExt:
            if not self.check_fext(self.__fext):
                raise FileError('invalid extension: "%s"' % self.__fext)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.fpath)

    def __str__(self):
        return self.read()

    @property
    def fpath(self):
        return self.__fpath

    @property
    def fname(self):
        return self.__fname

    @property
    def fext(self):
        return self.__fext

    def read(self):
        if self.__content is None:
            with open(self.__fpath, 'r') as fobj:
                self.__content = fobj.read()
        return self.__content

    def readlines(self):
        return self.read().splitlines()


class FileManager(object):

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
