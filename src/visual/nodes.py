from panda3d.core import NodePath

from direct.showbase.DirectObject import DirectObject


R_EXTERNAL = 0
R_INTERNAL = 1


class AngularNode(NodePath, DirectObject):

    def __init__(self, node):
        DirectObject.__init__(self)
        NodePath.__init__(self, 'AngularNode__%s' % node.getName())
        self.setPythonTag(self.__class__.__name__, self)

        self.__sourceNodePath = node
        self.__nodePathInst = node.copyTo(self)
        self.__centerMarker = self.attachNewNode('center')
        self.__centerMarker.setPos(self.getTightCenter())
        self.__axis = R_EXTERNAL

    @property
    def node(self):
        if self.getAxis() == R_INTERNAL:
            return self.__centerMarker
        else:
            return self

    def getDimensions(self):
        min_, max_ = self.getTightBounds()
        return max_ - min_

    def getCenter(self):
        return self.node().getBounds().getCenter()

    def getTightCenter(self):
        min_, max_ = self.getTightBounds()
        return min_ + (self.getDimensions() / 2)

    def getAxis(self):
        return self.__axis

    def setAxis(self, code):
        if code != self.getAxis():
            if code == R_EXTERNAL:
                axis, node = self.__nodePathInst, self.__centerMarker
            elif code == R_INTERNAL:
                axis, node = self.__centerMarker, self.__nodePathInst
            else:
                raise ValueError('invalid axis')

            axis.wrtReparentTo(self)
            node.wrtReparentTo(axis)
            self.__axis = code

    def copyTo(self, parentNodePath):
        aNodePath = self.__class__(self.__sourceNodePath)
        aNodePath.reparentTo(parentNodePath)
        aNodePath.setAxis(self.getAxis())
        aNodePath.setPosHprScale(self.getPos(), self.getHpr(), self.getScale())
        aNodePath.node.setHpr(self.node.getHpr())
        return aNodePath

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        NodePath.removeNode(self)
