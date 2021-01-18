__all__ = ['control', 'core', 'scene']


import builtins
import ctypes
import importlib
import sys
import types

from typing import Iterable

from panda3d import core as p3d


class _(type):

    def __new__(cls, name, bases, dct, **kwargs):
        """
        Returns a global singleton object to be used in lieu of the module.
        """
        dct['__module__'] = None
        name = dct['__qualname__'] = __package__

        if not hasattr(builtins, name):
            setattr(builtins, name, super().__new__(cls, name, bases, dct))

        return getattr(builtins, name)

    def __init__(cls, name, bases, dct, *,
                 submodules = Iterable[str],
                 ) -> type:
        """
        Set up the singleton by essentially mirroring the package itself.
        """
        super().__init__(name, bases, dct)

        for _name in submodules:
            module = importlib.import_module(f'{__package__}.{_name}')
            setattr(cls, _name, module)

        path = p3d.DSearchPath()
        for _path in sys.path:
            path.append_directory(_path)

        cls.store = cls.control.FileManager(path)


class _(object, metaclass = _, submodules = __all__):
    pass


_build_class = builtins.__build_class__


ctypes.pythonapi.PyEval_EvalCodeEx.restype = ctypes.py_object
ctypes.pythonapi.PyEval_EvalCodeEx.argtypes = (
    [ctypes.py_object] * 3
    + [ctypes.c_void_p, ctypes.c_int] * 3
    + [ctypes.c_void_p, ctypes.py_object]
    )


def build_class(body, name, *bases, **kwargs):
    """
    Post-processing for classes defined in this module. Any method defined in
    snake_case will be automatically aliased to camelCase as well. This is
    particularly useful when subclassing C-based types; i.e. NodePath,
    insomuch as it effectively overrides both entry points provided by Panda.
    """
    spec = body.__globals__.get('__spec__')

    if spec and (spec.name.split('.')[0] == __package__):
        metaclass = kwargs.pop('metaclass', type)
        namespace = metaclass.__prepare__(name, bases, **kwargs)
        classcell = ctypes.pythonapi.PyEval_EvalCodeEx(
            body.__code__, body.__globals__, namespace,
            None, 0, None, 0, None, 0,
            None, body.__closure__,
            )
    else:
        return _build_class(body, name, *bases, **kwargs)

    dct = {}
    for attr in namespace:
        if isinstance(
            namespace[attr],
            (types.FunctionType, classmethod, staticmethod),
            ):
            if attr.startswith('_'):
                continue

            words = attr.split('_')
            if attr.islower() and len(words) > 1:
                words[1:] = map(str.title, words[1:])
                dct[attr] = ''.join(words)


    for attr, alias in dct.items():
        func = namespace[attr]
        if isinstance(func, (staticmethod, classmethod)):
            f = func
        else:
            co = func.__code__.replace(co_name = f'{name}.{alias}')
            f = types.FunctionType(
                co,
                func.__globals__,
                co.co_name,
                func.__defaults__,
                func.__closure__,
                )
            f.__kwdefaults__ = func.__kwdefaults__
        namespace.setdefault(alias, f)
    return metaclass.__call__(metaclass, name, bases, namespace, **kwargs)


builtins.__build_class__ = build_class
