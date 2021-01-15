#!/usr/local/bin/python3.9

import collections

from panda3d import core as p3d

from direct.gui.DirectButton import DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.showbase.ShowBase import ShowBase

from src import nodes

from src.control.FileManager import FileManager


STORAGE_PATH = 'palettes/storage/walls'


class WallCarousel(ShowBase):

    def makeArrows(self):
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

    def makeScene(self):
        self.wall_maker = p3d.CardMaker('wall_maker')
        self.wall_maker.setFrame(0, 1, 0, 1)
        self.wall_pieces = collections.deque()
        self.current_piece = None
        self.current_piece_label = DirectLabel(
            parent = aspect2d,
            pos = (0, 0, -0.87),
            scale = (1.0 / 10, 1, 1.0 / 8),
            )

        files = list(FileManager().load(STORAGE_PATH))
        while files:
            tex_path = files.pop(0)

            if tex_path.fname.endswith('_a'):
                alpha_path = files.pop(0).fpath
            else:
                alpha_path = None

            piece = self.makeWall(tex_path.fpath, alpha_path)
            self.wall_pieces.append(piece)

        self.accept('arrow_right', self.rotate, extraArgs = [-1])
        self.accept('arrow_left', self.rotate, extraArgs = [1])
        self.rotate(-1)

    def makeWall(self, tex_path, alpha_path):
        tex = loader.loadTexture(tex_path, alpha_path)
        frame = hidden.attachNewNode(self.wall_maker.generate())
        frame.setName(tex.getName())
        frame.setTexture(tex)
        frame.setTransparency(p3d.TransparencyAttrib.MBinary)
        frame.setTwoSided(True)
        return frame

    def rotate(self, direction: int):
        self.wall_pieces.rotate(direction)

        if self.current_piece:
            self.current_piece.removeNode()
            del self.current_piece

        self.current_piece = self.wall_pieces[0].copyTo(render2d)
        self.current_piece.setPos(-0.5, 0, -0.5)
        self.current_piece_label.setText(self.current_piece.getName())


if __name__ == '__main__':
    app = WallCarousel()
    app.makeArrows()
    app.makeScene()
    app.run()
