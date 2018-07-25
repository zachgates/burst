import importlib


__all__ = ['FileManager', 'ObjectManager', 'SelectionManager']


for submodule in __all__:
    importlib.import_module('.' + submodule, __name__)
