from panda3d import core as p3d
from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def run(self):
        scene = burst.load_scene_2d('sample.burst')
        seqNode = p3d.SequenceNode('sprite')
        for n in (275, 279, 277, 278):
            seqNode.addChild(scene.make_tile(n).node())
        seqNode.setFrameRate(12)
        seqNode.pingpong(True)
        seqNP = aspect2d.attachNewNode(seqNode)
        super().run()


app = TestApp()
app.run()
