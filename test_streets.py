#!/usr/local/bin/python3.9

from tests import SlideShowBase


class StreetSlideShow(SlideShowBase):

    def run(self):
        streets = loader.load_model('storage/palettes/streets.bam')
        for node in streets.get_children():
            node = burst.core.AngularNode(
                parent = render,
                node = node,
                prefix = '',
                )
            node.reparent_to(render)
            node.hide()
            node.set_pos(-node.get_tight_center())
            self.slides.append(node)

        self.camera.set_pos(0, -6, 210)
        self.camera.set_hpr(0, -90, 0)
        self.disable_mouse()
        self.rotate(-1)
        super().run()


if __name__ == '__main__':
    app = StreetSlideShow()
    app.run()
