from panda3d.core import LPoint3f, NodePath


class OrbitalNode(NodePath):

    _delegated = (
        'getH',
        'setH',
        'getP',
        'setP',
        'getR',
        'setR',
        'getHpr',
        'setHpr',
        'hprInterval',
        'printHpr',
    )

    def __init__(self, model):
        super(OrbitalNode, self).__init__(model.getName())
        self.__model = model
        self.__render = self.__model.copyTo(self)

        self.__center = NodePath('center')
        self.__center.reparentTo(self)
        self.__center.setPos(self.getCenter())

        self.__orbitingCenter = False

    def __getattribute__(self, attr):
        if (attr in OrbitalNode._delegated) and self.isOrbitingCenter():
            return getattr(self.__center, attr)
        else:
            return super(OrbitalNode, self).__getattribute__(attr)

    def getCenter(self):
        bot, top = self.__render.getTightBounds()
        centerX = bot[0] + (top[0] - bot[0]) / 2
        centerY = bot[1] + (top[1] - bot[1]) / 2
        centerZ = bot[2] + (top[2] - bot[2]) / 2
        return LPoint3f(centerX, centerY, centerZ)

    def setOrbitCenter(self, bool_):
        if bool(bool_) is not self.isOrbitingCenter():
            if self.isOrbitingCenter():
                self.__render.wrtReparentTo(self)
                self.__center.wrtReparentTo(self.__render)
            else:
                self.__center.wrtReparentTo(self)
                self.__render.wrtReparentTo(self.__center)

            self.__orbitingCenter = bool_

    def isOrbitingCenter(self):
        return bool(self.__orbitingCenter)

    def copyTo(self, parent):
        node = self.__class__(self.__model)
        node.reparentTo(parent)
        node.setPosHprScale(self.getPos(), self.getHpr(), self.getScale())
        node.setOrbitCenter(self.isOrbitingCenter())
        return node
