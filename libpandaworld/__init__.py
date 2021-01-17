#!/usr/local/bin/python3.9

import builtins
import ctypes
import types


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
    ALL_CAPS will be processed into both snake_case and camelCase aliases.
    This is particularly useful when subclassing C-based types; i.e. NodePath,
    insomuch as it effectively overrides both entry points provided by Panda.
    """
    if not (
        (spec := body.__globals__.get('__spec__'))
        and (spec.name.split('.')[0] == __package__)
        ):
        return _build_class(body, name, *bases, **kwargs)
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
            if attr.isupper():
                aliases = dct[attr] = []
                (words := [])[:] = map(str.lower, attr.split('_'))
                aliases.append('_'.join(words))
                words[1:] = map(str.title, words[1:])
                aliases.append(''.join(words))


    for attr, aliases in dct.items():
        func = namespace[attr]
        for alias in aliases:
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
        del namespace[attr]
    return metaclass.__call__(metaclass, name, bases, namespace, **kwargs)


builtins.__build_class__ = build_class
