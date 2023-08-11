__all__ = [
    'PandaWidget',
]


from panda3d import core as p3d

from PyQt5 import QtCore, QtGui, QtWidgets


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
