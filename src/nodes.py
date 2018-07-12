from panda3d.core import NodePath

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


A_EXTERNAL = 0
A_INTERNAL = 1

N_ORIG = 0
N_COPY = 1
N_INST = 2


class AngularNode(DirectObject, NodePath):

    notify = DirectNotifyGlobal.directNotify.newCategory('AngularNode')

    def __init__(self, np, parentNP=None, mode=N_ORIG):
        DirectObject.__init__(self)
        NodePath.__init__(self, self.__class__.__name__ + '-' + np.getName())

        if parentNP is None:
            parentNP = np.getParent()

        self.reparentTo(parentNP)
        self.setPythonTag(self.__class__.__name__, self)
        self.setPosHprScale(np.getPos(parentNP),
                            np.getHpr(parentNP),
                            np.getScale(parentNP))

        if mode == N_ORIG:
            np.reparentTo(self)
        elif mode == N_COPY:
            np = np.copyTo(self)
        elif mode == N_INST:
            np = np.instanceTo(self)
        else:
            self.notify.error('got invalid mode: %i' % mode)

        self.__nodePathInst = np
        self.__nodePathInst.setPos(0, 0, 0)

        self.__centerMarker = self.attachNewNode('center')
        self.__centerMarker.setPos(render, self.getTightCenter())
        self.__axis = A_EXTERNAL

    def getNode(self):
        if self.getAxis() == A_INTERNAL:
            return self.__centerMarker
        else:
            return self

    def getDimensions(self):
        min_, max_ = self.getTightBounds()
        return max_ - min_

    def getCenter(self):
        return self.getNode().getBounds().getCenter()

    def getTightCenter(self):
        min_, max_ = self.getTightBounds()
        return min_ + (self.getDimensions() / 2)

    def getTransform(self):
        return self.getAxis(), self.getHpr(), self.getNode().getHpr()

    def setTransform(self, axis=None, topRot=None, botRot=None):
        if isinstance(axis, (tuple, list)) and len(axis) == 3:
            axis, topRot, botRot = axis
        else:
            self.notify.error('invalid transform')

        if axis:
            self.setAxis(axis)

        if topRot:
            self.setHpr(topRot)

        if botRot:
            self.getNode().setHpr(botRot)

    def getAxis(self):
        return self.__axis

    def setAxis(self, code):
        if code == self.getAxis():
            return

        if code == A_EXTERNAL:
            axis, node = self.__nodePathInst, self.__centerMarker
        elif code == A_INTERNAL:
            axis, node = self.__centerMarker, self.__nodePathInst
        else:
            self.notify.error('got invalid axis: %i' % code)

        axis.wrtReparentTo(self)
        node.wrtReparentTo(axis)
        self.__axis = code

    def copyTo(self, parentNP):
        aNodePath = self.__class__(self.__nodePathInst, parentNP, N_COPY)
        aNodePath.setTransform(self.getTransform())
        return aNodePath

    def instanceTo(self, parentNP):
        aNodePath = self.__class__(self.__nodePathInst, parentNP, N_INST)
        aNodePath.setTransform(self.getTransform())
        return aNodePath

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        NodePath.removeNode(self)
