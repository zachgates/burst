#!/usr/local/bin/python3.9

import collections
import re

from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.ShowBase import ShowBase

from src import nodes
from tests.SlideShowBase import SlideShowBase


STREETS_PATH = 'palettes/storage/streets.bam'


class StreetSlideShow(SlideShowBase):

    def run(self):
        for node in loader.load_model(STREETS_PATH).get_children():
            node = nodes.AngularNode(render, np = node)
            node.reparent_to(render)
            node.hide()
            node.set_pos(-node.getTightCenter())
            self.slides.append(node)

        self.camera.setPos(0, -6, 210)
        self.camera.setHpr(0, -90, 0)
        self.disableMouse()
        self.rotate(-1)
        super().run()


if __name__ == '__main__':
    app = StreetSlideShow()
    app.run()
