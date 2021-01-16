#!/usr/local/bin/python3.9

import collections

from panda3d import core as p3d

from src.control.FileManager import FileManager

from tests.SlideShowBase import SlideShowBase


WALLS_PATH = 'palettes/storage/walls'


class WallSlideShow(SlideShowBase):

    def __init__(self):
        super().__init__()
        self.wall_frame = p3d.CardMaker('wall_frame')
        self.wall_frame.set_frame(0, 1, 0, 1)
        self.file_store = FileManager()

    def run(self):
        files = self.file_store.load_directory(
            WALLS_PATH,
            extensions = ['.jpg'],
            )

        for file in files:
            alpha = file.path.with_suffix('.rgb')
            if alpha := self.file_store.find_file(alpha):
                alpha = self.file_store.load_file(alpha)

            wall = render2d.attach_new_node(self.wall_frame.generate())
            wall.set_name(file.path.stem)
            wall.set_texture(file.load(alpha_file = alpha))
            wall.set_transparency(p3d.TransparencyAttrib.M_binary)
            wall.set_pos(-0.5, 0, -0.5)
            wall.hide()
            self.slides.append(wall)

        self.rotate(-1)
        super().run()


if __name__ == '__main__':
    app = WallSlideShow()
    app.run()
