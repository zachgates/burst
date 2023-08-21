import burst
import dataclasses
import random

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.character import Character, Sprite, SpriteData
from burst.distributed import ClientRepository


class BurstApp(ShowBase):

    def build_spring(self):
        scene = base.cr.scene_manager.get_scene()
        spring = scene.make_sprite(SpriteData(
            name = 'spring',
            tracks = [
                Sprite.Track(
                    name = 'Bounce',
                    cells = [(6, 22), (6, 23), (6, 24)],
                    frame_rate = 12,
                    ),
                ],
            blend = p3d.LColor(60, 45, 71, 255),
            ))

        springNP = scene.get_background().attach_new_node(spring)
        springNP.set_bin('prop', 1)
        springNP.set_transparency(p3d.TransparencyAttrib.MAlpha)
        springNP.set_pos(random.choice([-1, 1]) * min(0.8, random.random()), 0, -min(0.8, max(0.1, random.random())))

        factor = 4
        springNP.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        spring.pingpong('Bounce')

    def respawn(self):
        for char in self.chars:
            char.set_action('Dead')
        self.spawn()

    def spawn(self):
        scene = base.cr.scene_manager.get_scene()
        self.chars.append(char := base.cr.createDistributedObject(
            className = 'Character',
            zoneId = base.cr.scene_manager.get_zone(),
            ))
        char.set_bin('char', 1)
        char.b_set_sprite(dataclasses.astuple(SpriteData(
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
            )))
        char.set_active(True)
        char.set_speed_factor(0.05 + random.randint(0, 100) * 0.001)
        char.startPosHprBroadcast(period = (1 / scene.get_frame_rate()))
        # self.accept_once('d', lambda: base.cr.sendDeleteMsg(self.char.doId))

    def setup_scene(self, zone):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)

        bgNP = scene.get_background()
        bgNP.set_texture(scene.get_tile(row = 1, column = 1))
        self.accept('p', scene.get_background().ls)

        scene.add_layer('prop')
        self.accept('b', self.build_spring)

        scene.add_layer('char')
        self.accept('g', self.spawn)
        self.accept('r', self.respawn)

        self.chars = []
        self.spawn()

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample2.burst2d', self.setup_scene)

    def run(self):
        self.cr = ClientRepository(['data/dclass/direct.dc', 'data/dclass/burst.dc'])
        self.cr.accept('scene-manager-ready', self.setup)
        super().run()


if __name__ == '__main__':
    base = BurstApp()
    base.run()
