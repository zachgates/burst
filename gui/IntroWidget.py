__all__ = [
    'IntroWidget',
]


import functools

from PyQt5 import QtCore, QtWidgets


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
