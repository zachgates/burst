import burst
import pprint

import panda3d.core as p3d

from direct.fsm.FSM import FSM, RequestDenied
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait
from direct.interval.LerpInterval import LerpPosInterval
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase

from burst.char import Sprite


class Player(FSM, DirectObject):

    def __init__(self, char, charNP):
        DirectObject.__init__(self)
        self.char = char
        self.charNP = charNP

        FSM.__init__(self, 'PlayerFSM')
        self.defaultTransitions = {
            'Idle' : ['Jump', 'Move', 'Dead'],
            'Jump' : ['Idle'],
            'Move' : ['Idle', 'Move'],
            'Dead' : [],
        }

        self.accept('escape', self.request, extraArgs = ['Dead'])

        self.accept('space', self.request, extraArgs = ['Jump'])
        self.accept('space-repeat', self.request, extraArgs = ['Jump'])

        self.accept('arrow_up', self.request, extraArgs = ['Move', p3d.Vec3(0, 0, 1)])
        self.accept('arrow_up-repeat', self.request, extraArgs = ['Move', p3d.Vec3(0, 0, 1)])

        self.accept('arrow_down', self.request, extraArgs = ['Move', p3d.Vec3(0, 0, -1)])
        self.accept('arrow_down-repeat', self.request, extraArgs = ['Move', p3d.Vec3(0, 0, -1)])

        self.accept('arrow_right', self.request, extraArgs = ['Move', p3d.Vec3(1, 0, 0)])
        self.accept('arrow_right-repeat', self.request, extraArgs = ['Move', p3d.Vec3(1, 0, 0)])

        self.accept('arrow_left', self.request, extraArgs = ['Move', p3d.Vec3(-1, 0, 0)])
        self.accept('arrow_left-repeat', self.request, extraArgs = ['Move', p3d.Vec3(-1, 0, 0)])

    def request(self, request, *args):
        try:
            super().request(request, *args)
        except RequestDenied as exc:
            pass

    def enterIdle(self):
        self.char.loop('Idle')

    def exitIdle(self):
        pass

    def enterJump(self):
        self.lerp = Sequence(
            Func(self.char.play, 'Jump'),
            Wait(0.5),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitJump(self):
        pass

    def enterMove(self, vec: p3d.Vec3):
        if hasattr(self, 'lerp'):
            return

        self.lerp = Sequence(
            Parallel(
                Func(self.char.play, 'Move'),
                self.charNP.posInterval(
                    (24 / 60),
                    pos = (self.charNP.get_pos()
                           + p3d.Vec3(
                               vec.x * self.charNP.get_sx(),
                               vec.y * self.charNP.get_sy(),
                               vec.z * self.charNP.get_sz(),
                               )),
                    startPos = self.charNP.get_pos(),
                    name = 'PlayerFSM-Move',
                    )),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitMove(self):
        pass

    def enterDead(self):
        self.char.loop('Dead')

    def exitDead(self):
        pass


if __name__ == '__main__':
    base = ShowBase()
    file = burst.store.load_file('tests/data/scenes/sample2.burst2d')
    scene = file.read()

    globalClock.set_mode(p3d.ClockObject.MLimited)
    globalClock.set_frame_rate(60)

    bgNP = scene.get_tile_card(row = 1, column = 1)
    bgNP.reparent_to(base.aspect2d)
    # bgNP.set_sx(3)

    char = Sprite(scene, 'sprite')
    char.set_blend(p3d.LColor(60, 45, 71, 255))
    char.add_track('Idle', [(10, 19), (10, 23), (10, 23), (10, 19)], frame_rate = 4)
    char.add_track('Jump', [(10, 19), (10, 23), (10, 22), (10, 21)], frame_rate = 10)
    char.add_track('Move', [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)], frame_rate = 24)
    char.add_track('Dead', [(10, 24)], frame_rate = 1)

    charNP = bgNP.attach_new_node(char)
    charNP.set_transparency(p3d.TransparencyAttrib.MAlpha)

    factor = 4
    charNP.set_scale(
        (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
        1,
        (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
        )

    fsm = Player(char, charNP)
    fsm.request('Idle')

    base.run()
