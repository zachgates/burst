import burst

from direct.showbase.ShowBase import ShowBase


class BurstApp(ShowBase):

    def run(self):
        scene = burst.store.load_file('data/scenes/sample1.burst2d').read()
        scene.set_frame_rate(60)

        sprite = burst.character.Sprite(scene, 'sprite')
        sprite.add_track(burst.character.Sprite.Track(
            name = 'Idle',
            cells = [(9, 19), (9, 23), (9, 22), (9, 21)],
            frame_rate = 8,
            ))
        sprite.loop('Idle')

        layer = scene.add_layer('char')
        layer.attach_new_node(sprite)

        super().run()


if __name__ == '__main__':
    base = BurstApp()
    base.run()
