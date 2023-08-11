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


burst.store.add_search_path(pathlib.Path(__file__).with_name('data'))
