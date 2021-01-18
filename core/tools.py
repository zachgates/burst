"""
The core tool functions, mostly for path-finding; also for loading files.
These functions get hooked to the global burst singleton object.
"""


_TILESPATH = None
_SCENEPATH = None


def get_root() -> burst.p3d.Filename:
    f_path = burst.p3d.Filename.from_os_specific(burst.__file__)
    return burst.p3d.Filename(f_path.get_dirname())


# Core TileSet Tools


def get_tile_path() -> burst.p3d.DSearchPath:
    global _TILESPATH
    if _TILESPATH is None:
        _TILESPATH = burst.p3d.DSearchPath(
            burst.p3d.Filename(burst.get_root(), 'tile/data'))
    return _TILESPATH


def find_tileset(f_name: str) -> burst.p3d.Filename:
    return burst.get_tile_path().find_file(f_name)


def load_tileset(f_name: str, **rules):
    f_path = burst.find_tileset(f_name)
    return burst.tile.TileSet(f_path, **rules)


# Core Scene Tools


def get_scene_path() -> burst.p3d.DSearchPath:
    global _SCENEPATH
    if _SCENEPATH is None:
        _SCENEPATH = burst.p3d.DSearchPath(
            burst.p3d.Filename(burst.get_root(), 'scene/data'))
    return _SCENEPATH


def find_scene2d(f_name: str) -> burst.p3d.Filename:
    return burst.get_scene_path().find_file(f_name)


def load_scene2d(f_name: str):
    Loader = burst.scene.SceneLoader2D()
    f_path = burst.find_scene2d(f_name)
    with Loader(f_path) as scene:
        return scene.read()


__all__ = [
    get_root,
    get_tile_path, find_tileset, load_tileset,
    get_scene_path, find_scene2d, load_scene2d,
]
