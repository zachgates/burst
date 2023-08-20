__all__ = [
    'character',
    'control',
    'core',
    'scene',
    'distributed',
    'ai',
]


import builtins
import ctypes
import importlib
import sys
import types

import panda3d.core as p3d


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
            if attr.startswith('_') or not attr.count('_'):
                continue

            if attr.islower():
                words = attr.split('_')
                words[1:] = map(str.title, words[1:])
                dct[attr] = str.join('', words)


    for attr, alias in dct.items():
        if isinstance(func := namespace[attr], (staticmethod, classmethod)):
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


_builtins__build_class__ = builtins.__build_class__
builtins.__build_class__ = build_class


class BurstModule(types.ModuleType):
    for name in __all__:
        exec(f'{name} = importlib.import_module("{__package__}.{name}")')


burst = sys.modules[__package__]
burst.__class__ = BurstModule
burst.store = burst.control.FileManager(
    p3d.get_model_path().operator_typecast_DSearchPath(),
    )
