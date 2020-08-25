import ctypes
import os
import platform

from typing import Optional, Union

from panda3d import core as p3d
from direct.directnotify import DirectNotifyGlobal


_WIN32: bool = (platform.system() == 'Windows')


class _DSO:
    """
    Primary C API interface for accessing a dynamic library.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory(__qualname__)

    if _WIN32:
        class WIN32API:
            from ctypes import wintypes as _wintypes
            # Loading dynamic libraries
            load = ctypes.windll.kernel32.LoadLibraryExW
            # Unloading libraries
            free = ctypes.windll.kernel32.FreeLibrary
            free.argtypes = [_wintypes.HMODULE]
            free.restype = _wintypes.BOOL
            # Accessing a handle for a library
            find = ctypes.windll.kernel32.GetModuleHandleW
            find.argtypes = [_wintypes.LPCWSTR]
            find.restype = _wintypes.HMODULE

    @classmethod
    def getErrorCode(self):
        # src/dtoolutil/load_dso.cxx L:66
        # // Returns the error message from the last failed load_dso() call.
        if _WIN32:
            return ctypes.windll.kernel32.GetLastError()
        # src/dtoolutil/load_dso.cxx L:139
        else:
            return ctypes.pythonapi.dlerror()

    def __init__(self, f_path: p3d.Filename):
        assert isinstance(f_path, p3d.Filename)
        self.__f_path: p3d.Filename = f_path
        self.__module: Optional[Union[ctypes.PyDLL, ctypes.WinDLL]] = None

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.__f_path.getFullpath()}")'

    def __getattr__(self, symbol: str):
        if self.__module is None:
            self.notify.warning(f'library not loaded: {self}')
            return (lambda *a, **kw: None)
        else:
            return getattr(self.__module, symbol)

    def get(self, _type, name: str):
        return _type.in_dll(self.__module, name)

    def load(self):
        f_path = self.__f_path.toOsSpecific()
        f_name = os.path.basename(f_path)
        # src/dtoolutil/load_dso.cxx L:52-53
        if _WIN32:
            # (0x8): LOAD_WITH_ALTERED_SEARCH_PATH
            buffer_path = ctypes.cast(f_path, ctypes.c_wchar_p)
            self.WIN32API.load(buffer_path, None, 0x8)
            # Access library
            buffer_name = ctypes.cast(f_name, ctypes.c_wchar_p)
            handle = self.WIN32API.find(buffer_name)
            self.__module = ctypes.WinDLL(f_name, handle=handle)
        # src/dtoolutil/load_dso.cxx L:128-129
        else:
            # (0x2): RTLD_NOW | (0x8): RTLD_GLOBAL
            self.__module = ctypes.PyDLL(f_path, 0x2 | 0x8)
            self.__module.dlclose.argtypes = [ctypes.c_long]

    def free(self):
        if self.__module is None:
            self.notify.error(f'library not yet loaded: {self}')

        # src/dtoolutil/load_dso.cxx L:61
        if _WIN32:
            # // true indicates success
            success = (self.WIN32API.free(self.__module._handle) != 0)
        # src/dtoolutil/load_dso.cxx L:134
        else:
            success = (self.__module.dlclose(self.__module._handle) == 0)

        self.__module = None
        return success


class DSOLoader(object):
    """
    // Loads in a dynamic library like an .so or .dll.  Returns NULL if
    // failure, otherwise on success.  If the filename is not absolute,
    // searches the path. If the path is empty, search the dtool directory.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory(__qualname__)

    # src/dtoolutil/load_dso.cxx L:35
    if _WIN32:
        # src/dtoolutil/load_dso.cxx L:83-94
        ERR_CODES = {
            2: 'file not found',
            3: 'path not found',
            4: 'too many open files',
            5: 'access denied',
            14: 'out of memory',
            18: 'no more files',
            126: 'module not found',
            127: 'the specified procedure could not be found',
            193: 'not a valid _WIN32 application',
            998: 'invalid access to memory location',
        }
    else:
        # See: DSOLoader.getErrorMsg
        from errno import errorcode as ERR_CODES

    # src/dtoolutil/load_dso.cxx L:64-100
    # src/dtoolutil/load_dso.cxx L:137-144
    @classmethod
    def getErrorMsg(cls, code: int) -> str:
        if code:
            # src/dtoolutil/load_dso.cxx L:83-99
            # src/dtoolutil/load_dso.cxx L:139-142
            return cls.ERR_CODES.get(code, os.strerror(code))
        # src/dtoolutil/load_dso.cxx L:143
        else:
            return 'no error'

    # src/dtoolutil/load_dso.cxx L:19-33
    @classmethod
    def resolve(cls,
                search_path: p3d.DSearchPath,
                f_path: p3d.Filename) -> p3d.Filename:
        # src/dtoolutil/load_dso.cxx L:20-29
        if f_path.isLocal():
            # src/dtoolutil/load_dso.cxx L:21-26
            if ((search_path.getNumDirectories() == 1)
                and (search_path.getDirectory(0) == '<auto>')):
                # src/dtoolutil/load_dso.cxx L:22-25
                # // This is a special case, meant to search in the same dir
                # // in which libp3dtool.dll, or the exe, was started from.
                d_tool_path = p3d.ExecutionEnvironment.getDtoolName()
                search_path = p3d.DSearchPath(os.path.dirname(d_tool_path))
            # src/dtoolutil/load_dso.cxx L:26-29
            return search_path.findFile(f_path)
        # src/dtoolutil/load_dso.cxx L:30-32
        else:
            return f_path

    def __init__(self, search_path: p3d.DSearchPath, f_name: p3d.Filename):
        if not isinstance(search_path, p3d.DSearchPath):
            self.notify.error('search_path must be of type DSearchPath')
        if not isinstance(f_name, p3d.Filename):
            self.notify.error('f_name must be of type Filename')
        # src/dtoolutil/load_dso.cxx L:48
        # src/dtoolutil/load_dso.cxx L:121
        self.__f_path: p3d.Filename = self.resolve(search_path, f_name)
        self.__module: _DSO = _DSO(self.__f_path)

    def __getattr__(self, symbol: str):
        return getattr(self.__module, symbol)

    # src/dtoolutil/load_dso.cxx L:119-130
    def load(self):
        # src/dtoolutil/load_dso.cxx L:49-51
        # src/dtoolutil/load_dso.cxx L:122-127
        if not self.__f_path.isRegularFile():
            # src/dtoolutil/load_dso.cxx L:123-125
            # // Make sure the error flag is cleared, to prevent a
            # // subsequent call to getErrorCode() from returning a
            # // previously stored error.
            code = self.__module.getErrorCode()
            self.notify.error(f'failed to load: {self.__module}: {code}')
        else:
            self.__module.load()
            self.notify.info(f'library loaded: {self.__module}')

    # src/dtoolutil/load_dso.cxx L:56-62
    # src/dtoolutil/load_dso.cxx L:132-135
    def free(self) -> bool:
        if not self.__module.free():
            self.notify.error(f'failed to release: {self.__module}')
        else:
            self.notify.info(f'library released: {self.__module}')
