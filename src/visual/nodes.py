from panda3d.core import NodePath


class PivotNode2D(NodePath):

    _modes = {
        0: (0, 0, 0),
        1: (180, 0, 0),
        2: (180, 0, 180),
        3: (0, 0, 180),
    }

    def __init__(self, model, parent=None):
        NodePath.__init__(self, model.getName())
        self.reparentTo(parent if parent else hidden)
        self._model = model
        self._mode = 0

        self.__pivot = NodePath('pivot')
        self.__pivot.reparentTo(self)

        self.__origin = NodePath('origin')
        self.__origin.reparentTo(self)

        self.__model = self._model.copyTo(self.__origin)
        self.__model.setTwoSided(True)

        a, b = self.__model.getTightBounds()
        center = (a[0] + ((b[0] - a[0]) / 2), 0, b[2] + ((a[2] - b[2]) / 2))
        self.__pivot.setPos(*center)

    def reorient(self, mode=0):
        if mode in PivotNode2D._modes:
            self._mode = mode
            self.__model.wrtReparentTo(self.__pivot)
            self.__pivot.setHpr(*PivotNode2D._modes.get(self._mode))
            self.__model.wrtReparentTo(self.__origin)
        return self

    def copyTo(self, parent):
        node = PivotNode2D(self._model, parent)
        node.setScale(self.getScale())
        node.reorient(self._mode)
        return node
