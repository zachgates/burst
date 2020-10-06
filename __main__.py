from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def run(self):
        self.scene = burst.loadScene2D('sample.burst')
        seqNode = burst.p3d.SequenceNode('sprite')
        for n in (307, 308, 309, 310):
            seqNode.addChild(self.scene.make_tile(n).node())
        seqNode.setFrameRate(12)
        seqNode.pingpong(True)
        seqNP = aspect2d.attachNewNode(seqNode)
        super().run()


app = TestApp()
app.run()
