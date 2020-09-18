from typing import Optional

from panda3d import core as p3d


_TILESPATH = None
_SCENEPATH = None


def getRoot() -> p3d.Filename:
    import burst
    f_path = p3d.Filename.fromOsSpecific(burst.__file__)
    return p3d.Filename(f_path.getDirname())


def getTilePath() -> p3d.DSearchPath:
    global _TILESPATH
    if _TILESPATH is None:
        _TILESPATH = p3d.DSearchPath(p3d.Filename(getRoot(), 'tile/data'))
    return _TILESPATH


def findTileset(f_name: str) -> Optional[p3d.Filename]:
    assert f_name
    return getTilePath().findFile(f_name)


def loadTileset(f_name: str, **rules):
    from ..tile import TileSet
    return TileSet(findTileset(f_name), **rules)


def getScenePath() -> p3d.DSearchPath:
    global _SCENEPATH
    if _SCENEPATH is None:
        _SCENEPATH = p3d.DSearchPath(p3d.Filename(getRoot(), 'scene/data'))
    return _SCENEPATH


def findScene2D(f_name: str) -> Optional[p3d.Filename]:
    assert f_name
    return getScenePath().findFile(f_name)


def loadScene2D(f_name: str):
    from ..scene import SceneLoader2D
    path = findScene2D(f_name)
    with SceneLoader2D(path) as loader:
        return loader.read()


__all__ = [
    getRoot,
    getTilePath, findTileset, loadTileset,
    getScenePath, findScene2D, loadScene2D,
]
