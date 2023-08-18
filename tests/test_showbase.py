import burst
import pprint

import panda3d.core as p3d

from direct.fsm.FSM import FSM, RequestDenied
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait
from direct.interval.LerpInterval import LerpPosInterval
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase

from burst.char import Sprite, Character


if __name__ == '__main__':
    base = ShowBase()
    file = burst.store.load_file('tests/data/scenes/sample2.burst2d')
    scene = file.read()

    globalClock.set_mode(p3d.ClockObject.MLimited)
    globalClock.set_frame_rate(60)

    bgNP = scene.get_tile_card(row = 1, column = 1)
    bgNP.reparent_to(base.aspect2d)
    bgNP.set_name('background')

    char = Sprite(scene, 'sprite')
    char.set_blend(p3d.LColor(60, 45, 71, 255))
    char.add_track('Idle', [(10, 19), (10, 23), (10, 23), (10, 19)], frame_rate = 4)
    char.add_track('Jump', [(10, 19), (10, 23), (10, 22), (10, 21)], frame_rate = 10)
    char.add_track('Move', [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)], frame_rate = 24)
    char.add_track('Dead', [(10, 24)], frame_rate = 1)

    charNP = Character(char)
    charNP.request('Idle')
    charNP.reparent_to(bgNP)
    charNP.set_transparency(p3d.TransparencyAttrib.MAlpha)

    factor = 4
    charNP.set_scale(
        (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
        1,
        (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
        )

    base.run()
