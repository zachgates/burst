__all__ = [
    'CharacterAI',
]


import collections
import dataclasses
import typing

from panda3d import core as p3d

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

from burst.character import Sprite, SpriteData


class CharacterAI(DistributedSmoothNodeAI):

    def __init__(self, air):
        print('CharacterAI.__init__')
        super().__init__(air)
        self._is_active = False
        self._sprite = None

    def generate(self):
        super().generate()
        print(f'new CharacterAI {self.doId}')

    def get_sprite(self) -> SpriteData:
        return self._sprite

    def set_sprite(self, data: SpriteData):
        self._sprite = data

    sprite = property(get_sprite, set_sprite)

    def get_active(self) -> bool:
        return self._is_active

    def set_active(self, is_active: bool):
        self._is_active = is_active
