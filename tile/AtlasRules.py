from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class AtlasRules(burst.core.RuleBase):

    tile_size: burst.core.Rule2D = None
    tile_run: burst.core.Rule2D = None
    tile_offset: burst.core.Rule2D = None

    def _typeCheck(self, name, type_):
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
