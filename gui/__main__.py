#!/usr/local/bin/python3

import functools
import sys

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from PyQt5 import QtCore, QtGui, QtWidgets


class IntroWidget(QtWidgets.QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.label = QtWidgets.QLabel('Choose a medium for your new project:')
        self.label.setAlignment(QtCore.Qt.AlignLeft)

        self.button2d = QtWidgets.QPushButton()
        self.button2d.setFixedSize(200, 200)
        self.button2d.setStyleSheet('background-image: url(gui/img/style2d-small.png)')
        self.button2d.clicked.connect(functools.partial(self.create, '2D'))

        self.button3d = QtWidgets.QPushButton()
        self.button3d.setFixedSize(200, 200)
        self.button3d.setStyleSheet('background-image: url(gui/img/style3d-small.png)')
        self.button3d.clicked.connect(functools.partial(self.create, '3D'))

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.button2d, 1, 0)
        self.grid.addWidget(self.button3d, 1, 1)
        self.grid.setContentsMargins(80, 40, 80, 40)

        self.setLayout(self.grid)
        self.setFixedSize(600, 320)

    def create(self, medium: str):
        self.close()
        self.app.exec_(medium)


class PandaWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        props = p3d.WindowProperties()
        props.setSize(self.size().width(), self.size().height())
        props.setUndecorated(True)
        props.setParentWindow(int(self.winId()))
        props.setForeground(False)
        base.openDefaultWindow(props = props)

        handle = base.win.getWindowHandle().getIntHandle()
        widget = QtWidgets.QWidget.createWindowContainer(
            QtGui.QWindow.fromWinId(handle),
            flags = QtCore.Qt.SubWindow,
            )

        self.setLayout(layout := QtWidgets.QVBoxLayout())
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        props = p3d.WindowProperties()
        props.setSize(self.size().width(), self.size().height())
        base.win.requestProperties(props)
        event.accept()


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
        layout.addWidget(PandaWidget(), 150)
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._window = QtWidgets.QMainWindow()
        self._window.setWindowTitle('Burst')
        self._window.setCentralWidget(widget)
        self._window.resize(800, 600)
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
