import burst
import pprint

import panda3d.core as p3d

from direct.fsm.FSM import FSM, RequestDenied
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait
from direct.interval.LerpInterval import LerpPosInterval
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase


class Player(FSM, DirectObject):

    def __init__(self, char):
        DirectObject.__init__(self)
        self.char = char

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

        self.accept('arrow_right', self.request, extraArgs = ['Move', 1])
        self.accept('arrow_right-repeat', self.request, extraArgs = ['Move', 1])

        self.accept('arrow_left', self.request, extraArgs = ['Move', -1])
        self.accept('arrow_left-repeat', self.request, extraArgs = ['Move', -1])

    def request(self, request, *args):
        try:
            super().request(request, *args)
        except RequestDenied as exc:
            pass

    def enterIdle(self):
        self.char.node.set_frame_rate(5)
        self.char.node.loop(True, 1, 4)

    def exitIdle(self):
        pass

    def enterJump(self):
        self.char.node.set_frame_rate(10)
        self.lerp = Sequence(
            Func(self.char.node.play, 13, 20),
            Wait(30 / 60),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitJump(self):
        pass

    def enterMove(self, direction):
        if hasattr(self, 'lerp'):
            return

        self.char.node.set_frame_rate(20)
        self.lerp = Sequence(
            Parallel(
                Func(self.char.node.play, 5, 12),
                self.char.np.posInterval(
                    (24 / 60),
                    pos = p3d.Point3(self.char.np.get_x() + direction, 0, 0),
                    startPos = self.char.np.get_pos(),
                    name = 'PlayerFSM-Move',
                    )),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitMove(self):
        pass

    def enterDead(self):
        self.char.node.pose(0)

    def exitDead(self):
        pass



    sprite = p3d.SequenceNode('sprite')
    sprite_np = base.aspect2d.attach_new_node(sprite)
    sprite_np.set_transparency(p3d.TransparencyAttrib.MAlpha)

    for i, cols in ((10, (24,)), # dead
                    (10, (19, 23, 23, 19)), # idle
                    (10, (19, 20, 21, 22, 22, 21, 20, 19)), # move
                    (10, (19, 23, 22, 21, 21, 22, 23, 19)), # jump
                    ):
        for j in cols:
            sprite.add_child(
                scene.make_tile((i, j), blend = (60, 45, 71, 255)).node())
def do_setup(scene):
    tex, bgNP = scene.make_tile(row = 1, column = 1)
    bgNP.reparent_to(base.aspect2d)
    bgNP.set_sx(3)

    globalClock.set_mode(p3d.ClockObject.MLimited)
    globalClock.set_frame_rate(60)
    char.node.set_frame_rate(20)

    fsm = Player(char)
    fsm.request('Idle')


if __name__ == '__main__':
    base = ShowBase()
    file = burst.store.load_file('tests/data/scenes/sample2.burst2d')
    scene = file.read()
    # file.write('tests/data/scenes/sample2.burst2d', scene)
    do_setup(scene)
    scene.run()
