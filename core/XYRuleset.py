from dataclasses import dataclass, astuple
from typing import Any, Generator, Mapping, Optional, Tuple

from direct.directnotify import DirectNotifyGlobal


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


@dataclass
class Rule(object):
    """
    Dataclass representing a single (X, Y) rule.
    """
    x: int = 0
    y: int = 0

    def __iter__(self):
        yield from astuple(self)


class XYRuleset:

    _RULES = ()
    _DEFAULTS = {}
    _NULL = Rule(0, 0)

    def __init__(self, **opts):
        super().__init__()
        self.__rules: Mapping[str, Tuple[int, int]] = {}

        for name, val in opts.items():
            self._set(name, val)

        for name in self._RULES:
            if name not in self.__rules:
                LOG.warning(f'rule not defined: "{name}"')
                self.clear()
                break
        else:
            LOG.info(f'defined rules: {self._RULES}')

    def __iter__(self) -> Generator[Tuple, None, None]:
        """
        Returns a (name, value) tuple of rules in the set.
        """
        yield from self.__rules.items()

    def __bool__(self) -> bool:
        """
        Determine if all rules are set.
        """
        return all(name in self.__rules for name in self._RULES)

    def _set(self, name: str, value: [Tuple, int]) -> bool:
        """
        Set a rule with its (x, y) values. Returns a boolean representing
        the operation's success.
        """
        if name in self._RULES:
            try:
                assert isinstance(value, (tuple, int))
                x, y = value
            except TypeError:
                x = y = value
            except (AssertionError, ValueError):
                LOG.warning(f'bad value for rule: "{name}": {repr(value)}')
            finally:
                self.__rules[name] = Rule(x, y)
                LOG.debug(f'set rule: "{name}" = {x, y}')
                return True
        else:
            LOG.warning(f'rule not defined: "{name}"')

        return False

    def __getattr__(self, name: str) -> Any:
        """
        Use attributes to access rules.
        """
        if name.startswith('_'):
            return super().__getattr__(self, name)
        else:
            return self.get(name)

    def get(self, name: str) -> Rule:
        """
        Returns a given rule. If the rule is not set or defined, returns NULL.
        """
        if name in self.__rules:
            return self.__rules[name]
        elif name in self._DEFAULTS:
            LOG.debug(f'rule not set: {name}')
            return self._DEFAULTS[name]
        else:
            LOG.warning(f'rule not defined: "{name}"')
            return self._NULL

    def reset(self, name: str, null: bool = False) -> bool:
        """
        Resets a given rule to its default. If no default is defined, the rule
        will be set to NULL. If the null argument is passed, the rule will be
        set to NULL.
        """
        if (name in self.__rules) or (name in self._RULES):
            value = self._DEFAULTS.get(name, self._NULL)
            self.__rules[name] = (self._NULL if null else value)
            return True
        else:
            LOG.warning(f'rule not defined: "{name}"')
            return False

    def clear(self, null: bool = False) -> bool:
        """
        Resets all rules to their defaults. If no defaults are defined, rules
        will be set to NULL.
        """
        return all(self.reset(name, null) for name in self._RULES)
