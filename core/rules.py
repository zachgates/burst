from contextlib import nullcontext
from dataclasses import dataclass, astuple
from typing import Iterable, get_type_hints


__all__ = ['RuleBase', 'Rule2D', 'Rule3D']


@dataclass(init=False)
class RuleBase:
    """
    Base class for dataclasses representing strict, typed rules.
    """

    def __iter__(self):
        yield from astuple(self)

    def __init__(self, **kwargs):
        for key, default, type_ in self._check_arg_types():
            with nullcontext(kwargs.get(key)) as val:
                if val is None:
                    val = type_()
                elif isinstance(val, Iterable):
                    val = type_(*val)
                else:
                    val = type_(val)
                self.__setattr__(key, val)

    def _check_arg_types(self):
        for name, type_ in get_type_hints(self).items():
            if type_:
                yield (name, self.__getattribute__(name), type_)


@dataclass
class Rule2D:
    """
    Two-dimensional (X, Y) integer rule.
    """
    x: int = 0
    y: int = 0


@dataclass
class Rule3D:
    """
    Three-dimensional (X, Y, Z) integer rule.
    """
    z: int = 0
