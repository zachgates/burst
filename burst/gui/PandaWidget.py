__all__ = [
    'PandaWidget',
]


from panda3d import core as p3d

from PyQt5 import QtCore, QtGui, QtWidgets


def size_to_panda_aspect_ratio(size: QtCore.QSize):
    if size.width() >= size.height():
        width = min(
            size.width(),
            ((size.height() * base.win.get_x_size())
             / base.win.get_y_size()
             ))
    else:
        width = size.width()
    height = ((width * base.win.get_y_size()) / base.win.get_x_size())
    return QtCore.QSize(width, height)


class PandaWidget(QtWidgets.QWidget):

    def test(self):
        print(
            f'{self = }',
            f'{self.metaObject().className() = }',
            f'{self.objectName() = }',
            f'{self.windowHandle() = }',
            f'{self.windowHandle().objectName() = }',
            '',
            f'{self.window() = }',
            f'{self.window().metaObject().className() = }',
            f'{self.window().objectName() = }',
            f'{self.window().windowHandle() = }',
            f'{self.window().windowHandle().objectName() = }',
            '',
            f'{self.parent() = }',
            f'{self.parent().metaObject().className() = }',
            f'{self.parent().objectName() = }',
            f'{self.parent().windowHandle() = }',
            f'{self.parent().windowHandle().objectName() = }',
            '',
            f'{self.container = }',
            f'{self.container.metaObject().className() = }',
            f'{self.container.objectName() = }',
            f'{self.container.windowHandle() = }',
            f'{self.container.windowHandle().objectName() = }',
            '',
            f'{self.container.window() = }',
            f'{self.container.window().metaObject().className() = }',
            f'{self.container.window().objectName() = }',
            f'{self.container.window().windowHandle() = }',
            f'{self.container.window().windowHandle().objectName() = }',
            '',
            f'{self.container.parent() = }',
            f'{self.container.parent().metaObject().className() = }',
            f'{self.container.parent().objectName() = }',
            f'{self.container.parent().windowHandle() = }',
            f'{self.container.parent().windowHandle().objectName() = }',
            '',
            f'{self.subwindow = }',
            f'{self.subwindow.metaObject().className() = }',
            f'{self.subwindow.objectName() = }',
            '',
            f'{self.subwindow.parent() = }',
            f'{self.subwindow.parent().metaObject().className() = }',
            f'{self.subwindow.parent().objectName() = }',
            '',
            sep = '\n',
            )

    def __init__(self, parent):
        super().__init__(parent)

        if base.win is None:
            props = p3d.WindowProperties.getConfigProperties()
            # print(self.size().width(), self.size().height())
            # props.setSize(self.size().width(), self.size().height())
            # props.setUndecorated(True)
            props.setParentWindow(int(self.winId())) # set a valid NSView pointer to prevent creating an NSWindow
            # props.setForeground(False)
            base.openDefaultWindow(props = props)
            # base.win.requestProperties(props)

        handle = base.win.getWindowHandle().getIntHandle()
        self.subwindow = QtGui.QWindow.fromWinId(handle)
        # self.subwindow.setFlags(QtCore.Qt.FramelessWindowHint)
        self.container = QtWidgets.QWidget.createWindowContainer(
            self.subwindow,
            # parent = self,
            flags = QtCore.Qt.SubWindow,
            )


        print(123, base.win.get_x_size(), base.win.get_y_size())
        print(self.size())
        print(self.container.size())
        print(self.subwindow.size())
        print(self.subwindow.parent().size())

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.container)
        # layout.setAlignment(QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        # set the correct(?) parent window handle
        props = p3d.WindowProperties.getConfigProperties()
        props.setParentWindow(int(self.container.winId()))
        # props.setOrigin(0, 0)
        base.win.requestProperties(props)

        # we need to trigger QWindowContainerPrivate.updateGeometry
        # so that the container calls window->setGeometry()

        print(dir(self.container.metaObject()))
        print()
        # print(self.baseSize())
        # print(self.container.baseSize())
        # print(self.subwindow.baseSize())
        # print(self.subwindow.parent().baseSize())

        # self.test()
        # print('------')
        # exit()

    def resizeEvent(self, event):
        """
        Mirror the aspect ratio of base.win to the container.
        """
        # print('resizeEvent')
        # FILL
        # Stretch Panda window to fill container
        # pass

        # FIT
        # Resize Panda window to fit container
        # props = p3d.WindowProperties()
        # props.setSize(self.subwindow.size().width(), self.subwindow.size().height())
        # base.win.requestProperties(props)

        # DEFER
        # Resize container to maintain Panda aspect ratio
        # self.container.resize(size_to_panda_aspect_ratio(self.size()))

        # print(type(event))
        print(self.size())
        print(self.container.size())
        print(self.subwindow.size())
        print(self.subwindow.parent().size())
        # self.resize(event.size())
        # self.subwindow.resize(event.size())
        print(event, event.oldSize(), event.size())
        print(self.size())
        print(self.container.size())
        print(self.subwindow.size())
        print(self.subwindow.parent().size())
        print()
        event.accept()
