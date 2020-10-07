"""
The global burst singleton object and its metaclass. The namespace of the
package itself becomes the namespace of the Burst class below.
"""

__all__ = ['core', 'scene', 'tile']


class _Burst(type):

    def __new__(cls, name, bases, dct):
        # Use builtins to store the burst singleton.
        import builtins
        # Create the global burst object.
        if not hasattr(builtins, 'burst'):
            builtins.burst = super().__new__(cls, name, bases, dct)
            builtins.burst.attach_modules()
            builtins.burst.attach_toolset()
        # Only ever return the singleton object.
        return builtins.burst

    def attach_modules(cls):
        from importlib import import_module
        # Hook the burst modules to the global burst object.
        for name in __all__:
            setattr(cls, name, import_module(f'Burst.{name}'))

    def attach_toolset(cls):
        # The tools module is not exported from core; import it for use here.
        import Burst.core.tools
        # Hook the core tool functions to the global burst object.
        for func in Burst.core.tools.__all__:
            setattr(cls, func.__name__, staticmethod(func))
        # Now remove tools from core; limiting use to explicit imports only.
        del Burst.core.tools


class Burst(metaclass = _Burst):

    __file__ = __file__

    from panda3d import core as p3d

    p3d.load_prc_file_data(
        """
        Burst module initial PRC data:
            - win-origin: puts the window at the center of the screen.
            - win-size: smallest possible; loading a scene adjusts the size.
            - textures-square: set none to support non-square tilesheets.
            - textures-power-2: set none to support non-power-of-2 tilesheets.
        """,
        """
        load-display pandagl
        win-origin -2 -2
        win-size 1 1
        fullscreen #f
        notify-level info
        textures-square none
        textures-power-2 none
        """)
