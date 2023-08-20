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
        super().__init__(air)
        self._sprite = SpriteData(
            name = 'sprite',
            tracks = [
                Sprite.Track(
                    name = 'Idle',
                    cells = [(10, 19), (10, 23), (10, 23), (10, 19)],
                    frame_rate = 4,
                    ),
                Sprite.Track(
                    name = 'Jump',
                    cells = [(10, 19), (10, 23), (10, 22), (10, 21), (10, 19)],
                    frame_rate = 10,
                    ),
                Sprite.Track(
                    'Move',
                    cells = [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)],
                    frame_rate = 24,
                    ),
                Sprite.Track(
                    name = 'Dead',
                    cells = [(10, 24)],
                    frame_rate = 1,
                    ),
            ],
            blend = p3d.LColor(60, 45, 71, 255),
            )

    def generate(self):
        super().generate()
        print('new CharacterAI')

    def get_sprite(self):
        return self._sprite

    def set_sprite(self, sprite: Sprite):
        self._sprite = sprite

    sprite = property(get_sprite, set_sprite)
