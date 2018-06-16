from panda3d.core import LPoint3f, NodePath


class OrbitalNode(NodePath):

    def __init__(self, model):
        NodePath.__init__(self, model.getName())
        self.__model = model

        self.__origin = NodePath('origin')
        self.__origin.reparentTo(self)
        self.__render = self.__model.copyTo(self.__origin)

        self.__center = NodePath('center')
        self.__center.reparentTo(self)
        self.__center.setPos(self.getCenter())

        self.__orbitingCenter = False
        self.__adjustDelegates()

    def __adjustDelegates(self):
        for funcName in dir(self):
            flatName = funcName.lower()
            if ('hpr' in flatName) and ('tex' not in flatName):
                delegate = getattr(self.getCenterNode(), funcName)
                setattr(self, funcName, delegate)

    def getCenter(self):
        bot, top = self.__render.getTightBounds()
        centerX = bot[0] + (top[0] - bot[0]) / 2
        centerY = bot[1] + (top[1] - bot[1]) / 2
        centerZ = bot[2] + (top[2] - bot[2]) / 2
        return LPoint3f(centerX, centerY, centerZ)

    def getCenterNode(self):
        if self.isOrbitingCenter():
            return self.__center
        else:
            return self.__origin

    def setOrbitCenter(self, bool_):
        if bool(bool_) is not self.isOrbitingCenter():
            if self.isOrbitingCenter():
                self.__render.wrtReparentTo(self.__origin)
                self.__center.wrtReparentTo(self.__render)
            else:
                self.__center.wrtReparentTo(self)
                self.__render.wrtReparentTo(self.__center)

            self.__orbitingCenter = bool(bool_)
            self.__adjustDelegates()

    def isOrbitingCenter(self):
        return self.__orbitingCenter

    def copyTo(self, parent):
        node = self.__class__(self.__model)
        node.reparentTo(parent)
        node.setPosHprScale(self.getPos(), self.getHpr(), self.getScale())
        node.setOrbitCenter(self.isOrbitingCenter())
        return node
