import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase


class SampleScene(ShowBase):

    def __init__(self):
        super().__init__()
        file = burst.store.load_file('tests/data/scenes/sample.burst2d')
        self.scene = file.read()

    def run(self):
        sprite = p3d.SequenceNode('sprite')
        for n in (307, 308, 309, 310):
            sprite.add_child(self.scene.make_tile(n).node())
        sprite.set_frame_rate(12)
        sprite.pingpong(True)
        aspect2d.attach_new_node(sprite)
        super().run()


if __name__ == '__main__':
    app = SampleScene()
    app.run()
