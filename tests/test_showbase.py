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

    def __init__(self, node, np):
        self.node = node
        self.np = np

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
        self.node.set_frame_rate(5)
        self.node.loop(True, 1, 4)

    def exitIdle(self):
        pass

    def enterJump(self):
        self.node.set_frame_rate(10)
        self.lerp = Sequence(
            Func(self.node.play, 13, 20),
            Wait(30 / 60),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitJump(self):
        pass

    def enterMove(self, direction):
        if hasattr(self, 'lerp'):
            return

        self.node.set_frame_rate(20)
        self.lerp = Sequence(
            Parallel(
                Func(self.node.play, 5, 12),
                self.np.posInterval(
                    (24 / 60),
                    pos = p3d.Point3(self.np.get_x() + direction, 0, 0),
                    startPos = self.np.get_pos(),
                    name = 'PlayerFSM-Move',
                    )),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def exitMove(self):
        pass

    def enterDead(self):
        self.node.pose(0)

    def exitDead(self):
        pass


class SampleScene(ShowBase):

    def __init__(self):
        super().__init__()
        file = burst.store.load_file('tests/data/scenes/sample.burst2d')
        self.scene = file.read()
        self.scene.adjust_window('sample', (512, 128))

    def run(self):
        globalClock.set_mode(p3d.ClockObject.MLimited)
        globalClock.set_frame_rate(60)

        sprite = p3d.SequenceNode('sprite')
        for i, cols in ((10, (24,)), # dead
                        (10, (19, 23, 23, 19)), # idle
                        (10, (19, 20, 21, 22, 22, 21, 20, 19)), # move
                        (10, (19, 23, 22, 21, 21, 22, 23, 19)), # jump
                        ):
            for j in cols:
                sprite.add_child(self.scene.make_tile((i, j), blend = (60, 45, 71, 255)).node())

        sprite.set_frame_rate(20)
        sprite_np = base.aspect2d.attach_new_node(sprite)
        sprite_np.set_transparency(p3d.TransparencyAttrib.M_alpha)

        player = Player(sprite, sprite_np)
        player.request('Idle')

        super().run()


if __name__ == '__main__':
    app = SampleScene()
    app.run()
