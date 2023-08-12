import burst

import panda3d.core as p3d

from direct.interval.IntervalGlobal import Func, Parallel, Sequence
from direct.interval.LerpInterval import LerpPosInterval
from direct.showbase.ShowBase import ShowBase


class SampleScene(ShowBase):

    def __init__(self):
        super().__init__()
        file = burst.store.load_file('tests/data/scenes/sample.burst2d')
        self.scene = file.read()
        self.scene.adjust_window('sample', (512, 128))

    def move_sprite(self, *extraArgs):
        if not hasattr(self, 'lerp'):
            self.lerp = Sequence(
                Parallel(
                    Func(self.sprite.play),
                    self.np.posInterval(
                        (24 / 60),
                        pos = p3d.Point3(self.np.get_x() + extraArgs[0], 0, 0),
                        startPos = self.np.get_pos(),
                        name = 'sprite-lerp',
                        )),
                Func(lambda: delattr(self, 'lerp')),
                ).start()

    def run(self):
        globalClock.set_mode(p3d.ClockObject.MLimited)
        globalClock.set_frame_rate(60)

        self.sprite = p3d.SequenceNode('sprite')
        for cell in ((10, 19),
                     (10, 20),
                     (10, 21),
                     (10, 22),
                     (10, 22),
                     (10, 21),
                     (10, 20),
                     (10, 19),
                     ):
            self.sprite.add_child(self.scene.make_tile(cell).node())
        self.sprite.set_frame_rate(20)
        self.np = base.aspect2d.attach_new_node(self.sprite)

        self.accept('space', self.sprite.play)
        self.accept('arrow_right', self.move_sprite, extraArgs = [1])
        self.accept('arrow_right-repeat', self.move_sprite, extraArgs = [1])
        self.accept('arrow_left', self.move_sprite, extraArgs = [-1])
        self.accept('arrow_left-repeat', self.move_sprite, extraArgs = [-1])

        super().run()


if __name__ == '__main__':
    app = SampleScene()
    app.run()
