__all__ = [
    'test_directstart',
    'test_showbase',
    'test_karts',
    'test_wheels',
    'test_streets',
    'test_walls',
    'test_vertices',
    'test_json',
]


import burst
import pathlib

from panda3d import core as p3d


burst.store.add_search_path(pathlib.Path(__file__).with_name('data'))

p3d.load_prc_file_data(
    "tests.__init__",
    """
    textures-auto-power-2 #f
    textures-power-2 #f
    """,
    )
