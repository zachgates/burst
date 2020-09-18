from collections.abc import Iterable
from dataclasses import dataclass

from ..core import RuleBase, Rule2D


@dataclass
class AtlasRules(RuleBase):

    tile_size: Rule2D = None
    tile_run: Rule2D = None
    tile_offset: Rule2D = None

    def _type_check(self, name, type_):
        attr = getattr(self, name)
        if isinstance(attr, int):
            value = type_.fill(attr)
        elif isinstance(attr, Iterable):
            args = tuple(attr)
            value = type_(*args)
        else:
            value = None

        value = (value if value else type_())
        setattr(self, name, value)
        return True
