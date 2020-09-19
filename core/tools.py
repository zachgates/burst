"""
The core tool functions, mostly for path-finding; also for loading files.
These functions get hooked to the global burst singleton object.
"""


_TILESPATH = None
_SCENEPATH = None


def getRoot() -> burst.p3d.Filename:
    f_path = burst.p3d.Filename.fromOsSpecific(burst.__file__)
    return burst.p3d.Filename(f_path.getDirname())


# Core TileSet Tools


def getTilePath() -> burst.p3d.DSearchPath:
    global _TILESPATH
    if _TILESPATH is None:
        _TILESPATH = burst.p3d.DSearchPath(
            burst.p3d.Filename(getRoot(), 'tile/data'))
    return _TILESPATH


def findTileset(f_name: str) -> burst.p3d.Filename:
    return getTilePath().findFile(f_name)


def loadTileset(f_name: str, **rules):
    f_path = findTileset(f_name)
    return burst.tile.TileSet(f_path, **rules)


# Core Scene Tools


def getScenePath() -> burst.p3d.DSearchPath:
    global _SCENEPATH
    if _SCENEPATH is None:
        _SCENEPATH = burst.p3d.DSearchPath(
            burst.p3d.Filename(getRoot(), 'scene/data'))
    return _SCENEPATH


def findScene2D(f_name: str) -> burst.p3d.Filename:
    return getScenePath().findFile(f_name)


def loadScene2D(f_name: str):
    Loader = burst.scene.SceneLoader2D()
    f_path = findScene2D(f_name)
    with Loader(f_path) as scene:
        return scene.read()


__all__ = [
    getRoot,
    getTilePath, findTileset, loadTileset,
    getScenePath, findScene2D, loadScene2D,
]
