import burst
import collections

import panda3d.core as p3d

from .gui import SlideShowBase


class WallSlideShow(SlideShowBase):

    def run(self):
        cm = p3d.CardMaker('wall_frame')
        cm.set_frame(-0.66, 0.66, -0.66, 0.66)

        for file in burst.store.load_directory('data/palettes/walls',
                                               extensions = ['.jpg'],
                                               ):
            self.slides.append(np := render2d.attach_new_node(cm.generate()))
            np.set_name(file.path.stem)
            np.set_texture(file.read(alpha = True))
            np.set_transparency(p3d.TransparencyAttrib.M_binary)
            np.hide()

        self.rotate(-1)
        super().run()


if __name__ == '__main__':
    app = WallSlideShow()
    app.run()
