import burst

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.character import Sprite, Character
from burst.distributed import ClientRepository


def setup_scene():
    file = burst.store.load_file('data/scenes/sample2.burst2d')
    scene = file.read()
    scene.set_frame_rate(60)

    bgNP = scene.get_tile_card(row = 1, column = 1)
    bgNP.reparent_to(base.aspect2d)
    bgNP.set_name('background')

    sprite = Sprite(scene, 'sprite')
    sprite.set_blend(p3d.LColor(60, 45, 71, 255))
    sprite.add_track('Idle', [(10, 19), (10, 23), (10, 23), (10, 19)], frame_rate = 4)
    sprite.add_track('Jump', [(10, 19), (10, 23), (10, 22), (10, 21), (10, 19)], frame_rate = 10)
    sprite.add_track('Move', [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)], frame_rate = 24)
    sprite.add_track('Dead', [(10, 24)], frame_rate = 1)

    charNP = Character(base.cr, sprite)
    base.cr.createDistributedObject(distObj = charNP, zoneId = 2)

    charNP.reparent_to(bgNP)
    charNP.set_transparency(p3d.TransparencyAttrib.MAlpha)
    charNP.set_speed_factor(0.05)

    factor = 4
    charNP.set_scale(p3d.Vec3(
        (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
        1,
        (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
        ))

    scale = (charNP.get_scale() - 1)
    charNP.set_bounds(
        p3d.Vec3(scale.get_x(), 0, scale.get_z()),
        p3d.Vec3(abs(scale.get_x()), 0, abs(scale.get_z())),
        )

    charNP.startPosHprBroadcast()


if __name__ == '__main__':
    base = ShowBase()
    base.cr = ClientRepository(['data/dclass/direct.dc', 'data/dclass/burst.dc'])
    base.cr.accept('client-joined', setup_scene)
    base.run()
