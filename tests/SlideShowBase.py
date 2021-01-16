#!/usr/local/bin/python3.9

import collections

from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.ShowBase import ShowBase


class SlideShowBase(ShowBase):

    def __init__(self):
        super().__init__(self)
        self.slides = collections.deque()
        self.slide_label = None
        self.setup()

    def setup(self):
        self.slide_label = DirectLabel(
            parent = aspect2d,
            pos = (0, 0, -0.87),
            scale = (1.0 / 10, 1, 1.0 / 8),
            )

        controls = loader.loadModel('shuttle_controls.egg')
        arrows = aspect2d.attachNewNode('gui_arrows')
        arrows.setPos(0, 0, -0.9)
        arrows.setScale(0.25)

        arrow_left_geom = controls.find('**/51')
        arrow_left_geom.node().removeGeom(0)
        arrow_left = DirectButton(
            parent = arrows,
            pos = (-5, 0, 0),
            geom = arrow_left_geom,
            geom_color = (0.8, 0, 0.1, 1),
            frameColor = (0, 0.5, 1, 1),
            pressEffect = True,
            command = self.rotate,
            extraArgs = [1],
            )

        self.accept('arrow_left', self.rotate, extraArgs = [1])
        self.accept('arrow_left-repeat', self.rotate, extraArgs = [1])

        arrow_right_geom = controls.find('**/52')
        arrow_right_geom.node().removeGeom(0)
        arrow_right = DirectButton(
            parent = arrows,
            pos = (4, 0, 0),
            geom = arrow_right_geom,
            geom_color = (0.8, 0, 0.1, 1),
            frameColor = (0, 0.5, 1, 1),
            pressEffect = True,
            command = self.rotate,
            extraArgs = [-1],
            )

        self.accept('arrow_right', self.rotate, extraArgs = [-1])
        self.accept('arrow_right-repeat', self.rotate, extraArgs = [-1])

    def rotate(self, direction: int):
        self.slides[0].hide()
        self.slides.rotate(direction)
        self.slides[0].show()
        self.slide_label.setText(self.slides[0].get_name())
