class _Burst(type):

    def __new__(cls, name, bases, dct):
        # Use builtins to store the burst singleton.
        import builtins

        # Create the global burst object.
        if not hasattr(builtins, 'burst'):
            builtins.burst = super().__new__(cls, name, bases, dct)
            builtins.burst.attach_tools()

        # Only ever return the singleton object.
        return builtins.burst

    def attach_tools(cls):
        # The tools module is not exported from core; import it for use here.
        import burst.core.tools

        # Hook the core tool functions to the global burst object.
        for func in burst.core.tools.__all__:
            setattr(cls, func.__name__, staticmethod(func))

        # Now remove tools from core; limiting use to explicit imports only.
        del burst.core.tools


class Burst(metaclass = _Burst):

    """
    The global burst singleton object. The module namespace becomes the
    namespace of this class.
    """

    from panda3d import core as p3d
    from . import core, scene, tile


    __file__ = __file__


    p3d.loadPrcFileData(
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
