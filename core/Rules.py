from dataclasses import dataclass, astuple
from typing import get_type_hints


class _Rule:
    """
    Base class for below dataclasses representing strict, typed rules.
    """

    @classmethod
    def fill(cls, val):
        n_args = len(cls.__dataclass_fields__)
        return cls(*(val,) * n_args)

    def __iter__(self):
        yield from astuple(self)

    def __post_init__(self):
        types = get_type_hints(self)
        for name, type_ in types.items():
            if getattr(self, name) is None:
                setattr(self, name, type_())
            else:
                assert self._type_check(name, type_)

    def _type_check(self, name, type_):
        attr = getattr(self, name)
        return isinstance(attr, type_)


@dataclass(frozen=True)
class Rule2D(_Rule):
    """
    Two-dimensional (X, Y) integer rule.
    """
    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class Rule3D(Rule2D):
    """
    Three-dimensional (X, Y, Z) integer rule.
    """
    z: int = 0
