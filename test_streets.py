#!/usr/local/bin/python3.9

import collections
import re

from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.ShowBase import ShowBase

from src import nodes


STORAGE_PATH = 'palettes/storage/streets.bam'


class StreetsCarousel(ShowBase):

    def makeScene(self):
        self.street_pieces = collections.deque()
        self.current_piece = None
        self.current_piece_label = DirectLabel(
            parent = aspect2d,
            pos = (0, 0, -0.87),
            scale = (1.0 / 10, 1, 1.0 / 8),
            )

        for node in loader.loadModel(STORAGE_PATH).getChildren():
            if match := re.fullmatch('^street_(.*)$', node.getName()):
                self.street_pieces.append((match.group(1), node))

        self.camera.setPos(0, -6, 210)
        self.camera.setHpr(0, -90, 0)
        self.disableMouse()

        self.accept('arrow_right', self.rotate, extraArgs = [-1])
        self.accept('arrow_left', self.rotate, extraArgs = [1])
        self.rotate(-1)

    def makeArrows(self):
        controls = loader.loadModel('shuttle_controls.egg')
        arrows = aspect2d.attachNewNode('gui-arrows')
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

    def rotate(self, direction: int):
        self.street_pieces.rotate(direction)

        if self.current_piece:
            self.current_piece.removeNode()
            del self.current_piece

        name, node = self.street_pieces[0]
        self.current_piece_label.setText(name)
        self.current_piece = nodes.AngularNode(render, np = node)
        self.current_piece.setAxis(nodes.A_INTERNAL)
        self.current_piece.setPos(-self.current_piece.getTightCenter())


if __name__ == '__main__':
    app = StreetsCarousel()
    app.makeScene()
    app.makeArrows()
    app.run()
