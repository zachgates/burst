import burst
import random

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.character import Sprite, Character
from burst.distributed import ClientRepository


class BurstApp(ShowBase):

    def setup_char(self, char):
        scene = base.cr.scene_manager.get_scene()

        char.reparent_to(self.bgNP)
        char.set_transparency(p3d.TransparencyAttrib.MAlpha)
        char.set_speed_factor(0.05 + random.random() * 0.1)

        factor = 4
        char.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        scale = (char.get_scale() - 1)
        char.set_bounds(
            p3d.Vec3(scale.get_x(), 0, scale.get_z()),
            p3d.Vec3(abs(scale.get_x()), 0, abs(scale.get_z())),
            )

        char.startPosHprBroadcast()
        self.accept('p', base.aspect2d.ls)

    def setup_scene(self, zone):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)

        self.bgNP = scene.make_tile_card(row = 1, column = 1)
        self.bgNP.reparent_to(base.aspect2d)
        self.bgNP.set_name('background')

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample2.burst2d', self.setup_scene)

    def run(self):
        self.cr = ClientRepository(['data/dclass/direct.dc', 'data/dclass/burst.dc'])
        self.cr.accept('scene-manager-ready', self.setup)
        self.cr.accept('character-ready', self.setup_char)
        super().run()


if __name__ == '__main__':
    base = BurstApp()
    base.run()
