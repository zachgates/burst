import builtins
import importlib

from panda3d import core as p3d


class _burst(type):
    def __new__(cls, name, bases, dct):
        for func in importlib.import_module('burst.core.tools').__all__:
            dct[func.__name__] = staticmethod(func)
        return super().__new__(cls, name, bases, dct)


class burst(metaclass = _burst):
    pass


builtins.burst = burst()
p3d.loadPrcFileData('burst',
    """
    load-display pandagl
    win-origin -2 -2
    win-size 1 1
    fullscreen #f
    notify-level info
    textures-square none
    textures-power-2 none
    """)
