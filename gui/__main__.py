#!/usr/local/bin/python3

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from PyQt5 import QtCore, QtGui, QtWidgets


class PandaWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        prop = p3d.WindowProperties()
        prop.setSize(self.size().width(), self.size().height())
        prop.setUndecorated(True)
        prop.setParentWindow(int(self.winId()))
        prop.setForeground(False)
        base.openDefaultWindow(props = prop)

        handle = base.win.getWindowHandle().getIntHandle()
        widget = QtWidgets.QWidget.createWindowContainer(
            QtGui.QWindow.fromWinId(handle),
            flags = QtCore.Qt.SubWindow,
            )

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def resizeEvent(self, event):
        prop = p3d.WindowProperties()
        prop.setSize(self.size().width(), self.size().height())
        base.win.requestProperties(prop)
        event.accept()


class BurstApp(QtWidgets.QApplication):

    def __init__(self):
        super().__init__([])
        base = ShowBase(windowType = 'none')
        base.disableMouse()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.addWidget(PandaWidget(), 150)
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

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

    def exec_(self):
        base.run()


if __name__ == '__main__':
    app = BurstApp()
    app.setup()
    app.exec_()
