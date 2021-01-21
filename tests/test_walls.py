#!/usr/local/bin/python3

import collections

from panda3d import core as p3d

from . import SlideShowBase


class WallSlideShow(SlideShowBase):

    def run(self):
        frame = p3d.CardMaker('wall_frame')
        frame.set_frame(0, 1, 0, 1)

        files = burst.store.load_directory(
            'tests/data/palettes/walls',
            extensions = ['.jpg'],
            )

        for file in files:
            try:
                alpha_path = file.path.with_suffix('.rgb')
                alpha_file = burst.store.load_file(alpha_path)
            except FileNotFoundError:
                alpha_file = None

            wall = render2d.attach_new_node(frame.generate())
            wall.set_pos(-0.5, 0, -0.5)
            wall.set_name(file.path.stem)
            wall.set_texture(file.read(alpha = alpha_file))
            wall.set_transparency(p3d.TransparencyAttrib.M_binary)
            wall.hide()
            self.slides.append(wall)

        self.rotate(-1)
        super().run()


if __name__ == '__main__':
    app = WallSlideShow()
    app.run()