import typing

from dataclasses import dataclass, astuple


__all__ = ['RuleBase', 'Rule2D', 'Rule3D']


class RuleBase:
    """
    Base class for dataclasses representing strict, typed rules.
    """

    @classmethod
    def fill(cls, val):
        n_args = len(cls.__dataclass_fields__)
        return cls(*(val,) * n_args)

    def __iter__(self):
        yield from astuple(self)

    def __post_init__(self):
        types = typing.get_type_hints(self)
        for name, type_ in types.items():
            if getattr(self, name) is None:
                setattr(self, name, type_())
            else:
                assert self._typeCheck(name, type_)

    def _typeCheck(self, name, type_):
        attr = getattr(self, name)
        return isinstance(attr, type_)


@dataclass(frozen=True)
class Rule2D(RuleBase):
    """
    Two-dimensional (X, Y) integer rule.
    """
    x: int = 0
    y: int = 0


@dataclass(frozen=True)
class Rule3D(RuleBase):
    """
    Three-dimensional (X, Y, Z) integer rule.
    """
    z: int = 0
