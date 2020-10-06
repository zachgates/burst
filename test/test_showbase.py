import Burst

from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def __init__(self):
        super().__init__()
        self._scene = burst.loadScene2D('sample.burst')

    def run(self):
        seqNode = burst.p3d.SequenceNode('sprite')
        for n in (307, 308, 309, 310):
            seqNode.addChild(self._scene.make_tile(n).node())
        seqNode.setFrameRate(12)
        seqNode.pingpong(True)
        seqNP = aspect2d.attachNewNode(seqNode)
        super().run()


if __name__ == '__main__':
    base = TestApp()
    base.run()
