from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def __init__(self):
        super().__init__()
        self._scene = burst.load_scene2d('sample.burst')

    def run(self):
        sprite = burst.p3d.SequenceNode('sprite')
        for n in (307, 308, 309, 310):
            sprite.add_child(self._scene.make_tile(n).node())
        sprite.set_frame_rate(12)
        sprite.pingpong(True)
        aspect2d.attach_new_node(sprite)
        super().run()


app = TestApp()
app.run()
