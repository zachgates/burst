from panda3d import core as p3d


_TILESPATH = None
_SCENEPATH = None


def getRoot() -> p3d.Filename:
    f_path = p3d.Filename.fromOsSpecific(burst.__file__)
    return p3d.Filename(f_path.getDirname())


# Core TileSet Tools


def getTilePath() -> p3d.DSearchPath:
    global _TILESPATH
    if _TILESPATH is None:
        _TILESPATH = p3d.DSearchPath(p3d.Filename(getRoot(), 'tile/data'))
    return _TILESPATH


def findTileset(f_name: str) -> p3d.Filename:
    return getTilePath().findFile(f_name)


def loadTileset(f_name: str, **rules):
    f_path = findTileset(f_name)
    return burst.tile.TileSet(f_path, **rules)


# Core Scene Tools


def getScenePath() -> p3d.DSearchPath:
    global _SCENEPATH
    if _SCENEPATH is None:
        _SCENEPATH = p3d.DSearchPath(p3d.Filename(getRoot(), 'scene/data'))
    return _SCENEPATH


def findScene2D(f_name: str) -> p3d.Filename:
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
