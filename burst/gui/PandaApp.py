__all__ = [
    'PandaApp',
]


import abc
import burst

from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase

from PyQt5 import QtWidgets

from burst.gui import PandaWidget


class PandaApp(QtWidgets.QApplication, DirectObject):

    def __init__(self, argv):
        QtWidgets.QApplication.__init__(self, argv)
        DirectObject.__init__(self)

        notify = p3d.Notify.ptr()
        # notify.getCategory('display').setSeverity(p3d.NSDebug)
        notify.getCategory('windisplay').setSeverity(p3d.NSSpam)
        notify.getCategory('cocoadisplay').setSeverity(p3d.NSSpam)
        notify.getCategory('cocoagldisplay').setSeverity(p3d.NSSpam)

        base = ShowBase(windowType = 'none')
        # event from ShowBase._doOpenWindow
        self.accept('open_main_window', self.load)

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError()

    def exec_(self):
        if base.win is None:
            props = p3d.WindowProperties()
            # print(self.size().width(), self.size().height())
            # props.setSize(self.size().width(), self.size().height())
            props.setUndecorated(True)
            props.setParentWindow(int(self.window.winId()))
            props.setForeground(True)
            base.openDefaultWindow(props = props)

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('Burst')
        self.window.setCentralWidget(PandaWidget(base.win))
        self.window.show()
        self.window.raise_()

        center = self.desktop().availableGeometry().center()
        self.window.move(
            int(center.x() - (self.window.width() * 0.5)),
            int(center.y() - (self.window.height() * 0.5)),
            )

        base.disableMouse()
        base.run()
