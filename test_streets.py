#!/usr/local/bin/python3.9

import collections
import re

from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.ShowBase import ShowBase

from libpandaworld.nodes import AngularNode

from tests.SlideShowBase import SlideShowBase


STREETS_PATH = 'palettes/storage/streets.bam'


class StreetSlideShow(SlideShowBase):

    def run(self):
        for node in loader.load_model(STREETS_PATH).get_children():
            node = AngularNode(parent = render, node = node, prefix = '')
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
