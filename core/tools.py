from typing import Optional

from panda3d import core as p3d


_TILESPATH = None
_SCENEPATH = None


def get_root() -> p3d.Filename:
    import burst
    f_path = p3d.Filename(burst.__file__)
    return p3d.Filename(f_path.getDirname())


def get_tile_path() -> p3d.DSearchPath:
    global _TILESPATH
    if _TILESPATH is None:
        _TILESPATH = p3d.DSearchPath(p3d.Filename(get_root(), 'tile/data'))
    return _TILESPATH


def find_tileset(f_name: str) -> Optional[p3d.Filename]:
    assert f_name
    f_path = get_tile_path().findFile(f_name)
    return (f_path if f_path.exists() else None)


def load_tileset(f_name: str, **rules):
    from ..tile import TileSet
    return TileSet(find_tileset(f_name), **rules)


__all__ = [get_root, get_tile_path, find_tileset, load_tileset]
