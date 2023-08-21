import burst
import dataclasses
import random

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.character import Character, Sprite, SpriteData
from burst.distributed import ClientRepository


DEFAULT_SPRITE = SpriteData(
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


class BurstApp(ShowBase):

    def setup_scene(self, zone):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)
        scene.get_background().set_texture(
            scene.get_tile(row = 1, column = 1))

        char = base.cr.createDistributedObject(
            className = 'Character',
            zoneId = zone,
            )
        char.b_set_sprite(dataclasses.astuple(DEFAULT_SPRITE))
        char.set_active(True)
        char.set_speed_factor(0.05 + random.randint(0, 100) * 0.001)
        char.startPosHprBroadcast(period = (1 / scene.get_frame_rate()))

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample2.burst2d', self.setup_scene)

    def run(self):
        self.cr = ClientRepository(['data/dclass/direct.dc', 'data/dclass/burst.dc'])
        self.cr.accept('scene-manager-ready', self.setup)
        super().run()


if __name__ == '__main__':
    base = BurstApp()
    base.run()
