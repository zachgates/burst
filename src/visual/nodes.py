from panda3d.core import NodePath


R_EXTERNAL = False
R_INTERNAL = True


class AngularNode(NodePath):

    _delegates = (
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

    def __init__(self, node):
        NodePath.__init__(self, 'AngularNode__%s' % node.getName())
        self.setPythonTag(self.__class__.__name__, self)
        self.__sourceNodePath = node
        self.__nodePathInst = node.copyTo(self)
        self.__centerMarker = self.attachNewNode('center')
        self.__centerMarker.setPos(self.getTightCenter())
        self.__axis = R_EXTERNAL

    def __getattribute__(self, attr):
        if (attr in AngularNode._delegates) and (self.__axis == R_INTERNAL):
            return getattr(self.__centerMarker, attr)
        else:
            return NodePath.__getattribute__(self, attr)

    def getDimensions(self):
        min_, max_ = self.getTightBounds()
        return max_ - min_

    def getCenter(self):
        return self.node().getBounds().getCenter()

    def getTightCenter(self):
        min_, max_ = self.getTightBounds()
        return min_ + (self.getDimensions() / 2)

    def toggleAxis(self):
        if self.__axis == R_INTERNAL:
            axis, node = self.__nodePathInst, self.__centerMarker
        else:
            axis, node = self.__centerMarker, self.__nodePathInst

        axis.wrtReparentTo(self)
        node.wrtReparentTo(axis)
        self.__axis = not self.__axis

    def copyTo(self, parentNodePath):
        aNodePath = self.__class__(self.__sourceNodePath)
        aNodePath.reparentTo(parentNodePath)
        aNodePath.copyAllProperties(self)
        return aNodePath

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        NodePath.removeNode(self)
