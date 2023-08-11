#!/usr/local/bin/python3

import sys

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from PyQt5 import QtCore, QtGui, QtWidgets

from . import IntroWidget, PandaWidget


class BurstApp(QtWidgets.QApplication):

    def __init__(self):
        super().__init__(sys.argv)
        window = IntroWidget(self)
        window.show()
        super().exec_()

    def launch(self):
        base = ShowBase(windowType = 'none')
        base.disableMouse()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout := QtWidgets.QHBoxLayout())
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.addWidget(PandaWidget(), 200)
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._window = QtWidgets.QMainWindow()
        self._window.setWindowTitle('Burst')
        self._window.setCentralWidget(widget)
        self._window.resize(900, 600)
        self._window.show()
        self._window.raise_()

        center = self.desktop().availableGeometry().center()
        self._window.move(
            int(center.x() - self._window.width() * 0.5),
            int(center.y() - self._window.height() * 0.5),
            )

    def setup(self):
        model = loader.loadModel('smiley.egg')
        model.reparentTo(render)
        model.setPos(0, 10, 0)

    def exec_(self, medium: str):
        self.launch()
        self.setup()
        base.run()


if __name__ == '__main__':
    app = BurstApp()
    # app.setup()
    # app.exec_()
