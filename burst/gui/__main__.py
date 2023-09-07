import burst
import sys

from panda3d import core as p3d


class BurstApp(burst.gui.PandaApp):

    def load(self):
        # path = p3d.Filename('data/scenes/test.burst2d')
        # file = burst.scene.SceneFile2D(path)

        size = p3d.LVector2i(256, 256)
        scene = burst.scene.Scene2D('burst.gui', size, 60)
        # not handled correctly by Scene2D when using PyQt
        self.window.setWindowTitle('burst.gui')
        self.window.resize(size.x, size.y)

        scene.load_tilesheet(
            burst.store.load_file('data/tiles/tilesheet.png'),
            burst.core.TileSet.Rules(
                tile_size = p3d.LVector2i(16, 16),
                tile_run = p3d.LVector2i(32, 32),
                tile_offset = p3d.LVector2i(1, 1),
                ))

        sprite = burst.character.Sprite(None, scene, 'sprite') # cr is None
        sprite.set_tilesheet(0)
        sprite.add_track(burst.character.Sprite.Track(
            name = 'Idle',
            cells = [(9, 19), (9, 23), (9, 22), (9, 21)],
            frame_rate = 8,
            ))
        sprite.loop('Idle')
        sprite.reparent_to(scene.add_layer('char'))
        sprite.set_scale(1) # counter scale factor in Character


if __name__ == '__main__':
    burst.app = BurstApp(sys.argv)
    burst.app.exec_()
