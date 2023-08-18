__all__ = [
    'Character',
]


from panda3d import core as p3d

from direct.fsm.FSM import FSM, RequestDenied
from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait
from direct.showbase.DirectObject import DirectObject

from burst.char import Sprite


class Character(FSM, DirectObject, p3d.NodePath):

    def __init__(self, char: Sprite):
        FSM.__init__(self, 'CharacterFSM')
        DirectObject.__init__(self)
        p3d.NodePath.__init__(self, char)

        self.char = char
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

    def enterJump(self):
        self.lerp = Sequence(
            Func(self.char.play, 'Jump'),
            Wait(0.5),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def enterMove(self, vec: p3d.Vec3):
        if hasattr(self, 'lerp'):
            return

        self.lerp = Sequence(
            Parallel(
                Func(self.char.play, 'Move'),
                self.posInterval(
                    (24 / 60),
                    pos = (self.get_pos()
                           + p3d.Vec3(
                               vec.x * self.get_sx(),
                               vec.y * self.get_sy(),
                               vec.z * self.get_sz(),
                               )),
                    startPos = self.get_pos(),
                    name = 'Move',
                    )),
            Func(delattr, self, 'lerp'),
            Func(self.request, 'Idle'),
            ).start()

    def enterDead(self):
        self.char.loop('Dead')
