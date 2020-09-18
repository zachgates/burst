from panda3d.core import loadPrcFileData
loadPrcFileData('burst',
    """
    load-display pandagl
    win-origin -2 -2
    win-size 1 1
    fullscreen #f
    notify-level info
    textures-square none
    textures-power-2 none
    """)


import importlib
tools = importlib.import_module('burst.core.tools')
class burst:
    for func in tools.__all__:
        locals()[func.__name__] = staticmethod(func)


import builtins
builtins.burst = burst()
