__all__ = ['control', 'core', 'scene']


import builtins
import ctypes
import importlib
import sys
import types

from typing import Iterable

from panda3d import core as p3d


_builtins__build_class__ = builtins.__build_class__


ctypes.pythonapi.PyEval_EvalCodeEx.restype = ctypes.py_object
ctypes.pythonapi.PyEval_EvalCodeEx.argtypes = (
    [ctypes.py_object] * 3
    + [ctypes.c_void_p, ctypes.c_int] * 3
    + [ctypes.c_void_p, ctypes.py_object]
    )


class _(type):

    def __new__(cls, name, bases, dct, **kwargs):
        """
        Returns a global singleton object to be used in lieu of the module.
        """
        if not hasattr(builtins, name):
            setattr(builtins, name, super().__new__(cls, name, bases, dct))
        return getattr(builtins, name)

    def __init__(cls, name, bases, dct, /, *,
                 submodules: Iterable[str],
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
            path.append_directory(p3d.Filename.from_os_specific(_path))

        cls.store = cls.control.FileManager(path)



class burst(object, metaclass = _, submodules = __all__):
    pass


def build_class(body, name, *bases, **kwargs):
    """
    Post-processing for classes defined in this module. Any method defined in
    snake_case will be automatically aliased to camelCase as well. This is
    particularly useful when subclassing C-based types; i.e. NodePath,
    insomuch as it effectively overrides both entry points provided by Panda.
    """
    if not (
        (spec := body.__globals__.get('__spec__'))
        and (spec.name.split('.')[0] == __package__)
        ):
        return _builtins__build_class__(body, name, *bases, **kwargs)
    else:
        metaclass = kwargs.pop('metaclass', type)
        namespace = metaclass.__prepare__(name, bases, **kwargs)
        classcell = ctypes.pythonapi.PyEval_EvalCodeEx(
            body.__code__, body.__globals__, namespace,
            None, 0, None, 0, None, 0,
            None, body.__closure__,
            )

    dct = {}
    for attr in namespace:
        if isinstance(
            namespace[attr],
            (types.FunctionType, classmethod, staticmethod),
            ):
            if attr.startswith('_'):
                continue

            if attr.islower() and len(words := attr.split('_')) > 1:
                words[1:] = map(str.title, words[1:])
                dct[attr] = ''.join(words)


    for attr, alias in dct.items():
        func = namespace[attr]
        if isinstance(func, (staticmethod, classmethod)):
            f = func
        else:
            f = types.FunctionType(
                code := func.__code__.replace(
                    co_name = f'{name}.{alias}',
                    ),
                func.__globals__,
                code.co_name,
                func.__defaults__,
                func.__closure__,
                )
            f.__kwdefaults__ = func.__kwdefaults__
        namespace.setdefault(alias, f)
    return metaclass.__call__(metaclass, name, bases, namespace, **kwargs)


builtins.__build_class__ = build_class
