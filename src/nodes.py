from panda3d.core import NodePath, VBase3

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


A_EXTERNAL = 0
A_INTERNAL = 1

N_ORIG = 0
N_INST = 1
N_COPY = 2


class AngularNode(DirectObject, NodePath):

    notify = DirectNotifyGlobal.directNotify.newCategory('AngularNode')

    @classmethod
    def isAngular(cls, np):
        np = np.getPythonTag(cls.__name__) or np
        return isinstance(np, cls), np

    def __init__(self, parentNP=None, name=None, np=None, mode=N_ORIG):
        DirectObject.__init__(self)
        NodePath.__init__(self,
                          name or self.__class__.__name__ + '-%s' % \
                          ('empty' if np is None else np.getName()))
        self.setPythonTag(self.__class__.__name__, self)

        self.__axis = A_EXTERNAL
        self.__center = self.attachNewNode('center')
        self.__nodes = self.attachNewNode('nodes')
        self.__nextParent = hidden

        if parentNP is None:
            parentNP = hidden

        flag, parentNP = self.isAngular(parentNP)
        if flag:
            parentNP.attach(self)
        else:
            self.reparentTo(parentNP)

        self.__nextParent = self.getParent()
        if np is not None:
            self.attach(np, mode)

        s = loader.loadModel('smiley.egg.pz')
        s.reparentTo(self.__center)
        s.setScale(3)
        self.__center.setColor(0, 0, 1)

    def __iter__(self):
        for np in self.__nodes.getChildren():
            yield np

    # AngularNode helpers

    def getDimensions(self):
        bounds = self.getTightBounds()
        if bounds:
            min_, max_ = self.getTightBounds()
            return max_ - min_
        else:
            return VBase3(0, 0, 0)

    def getCenter(self):
        return self.__nodes.getBounds().getCenter()

    def getTightCenter(self):
        bounds = self.getTightBounds()
        if bounds:
            min_, max_ = bounds
            return min_ + (self.getDimensions() / 2)
        else:
            return VBase3(0, 0, 0)

    def _readjustCenter(self):
        self.__center.setPos(self.getCenter())

    def attach(self, np, mode=N_ORIG):
        if mode == N_ORIG:
            flag, np = self.isAngular(np)
            if flag:
                np.__nextParent = np.getParent()
        elif mode == N_INST:
            np = np.instanceTo(self.getParent())
        elif mode == N_COPY:
            np = np.copyTo(self.getParent())
        else:
            self.notify.error('got invalid mode: %i' % mode)
            return

        np.wrtReparentTo(self.__nodes)
        self._readjustCenter()
        return np

    # AngularNode getters

    def getKeys(self):
        return set(np.getKey() for np in self)

    def getFutureParent(self):
        return self.__nextParent

    def getAxis(self):
        return self.__axis

    def getTransform(self, np=None):
        if np is None: np = render
        return (self.getAxis(),
                self.getPos(np), self.getHpr(np),
                self.__nodes.getPos(), self.__nodes.getHpr())

    # AngularNode setters

    def setAxis(self, code):
        if code == A_EXTERNAL or code == A_INTERNAL:
            self.__axis = code
            self._readjustCenter()
        else:
            self.notify.error('got invalid axis: %i' % code)

    def setTransform(self,
                     axis=None,
                     topPos=None, topRot=None,
                     botPos=None, botRot=None,
                     np=None):
        try:
            axis, topPos, topRot, botPos, botRot = axis
        except TypeError:
            self.notify.error('invalid transform')
            return

        if np is None: np = render
        if axis: self.setAxis(axis)
        if topPos: self.setPos(parentNP, topPos)
        if topRot: self.setHpr(parentNP, topRot)
        if botPos: self.__nodes.setPos(botPos)
        if botRot: self.__nodes.setPos(botRot)

    # NodePath overloads

    def detachNode(self):
        flag, parentNP = self.isAngular(self.getParent())
        self.wrtReparentTo(self.getFutureParent())
        self.__nextParent = hidden

        if flag:
            parentNP._readjustCenter()

        return self

    def copyTo(self, parentNP):
        return self.__nodes.copyTo(parentNP)

    def instanceTo(self, parentNP):
        return self.__nodes.instanceTo(parentNP)

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        NodePath.removeNode(self)

    def getHpr(self, parentNP=None):
        if parentNP is None: parentNP = self
        if self.getAxis() == A_INTERNAL:
            return self.__center.getHpr(parentNP)
        else:
            return self.__nodes.getHpr(parentNP)

    def getH(self, parentNP=None): return self.getHpr(parentNP)[0]
    def getP(self, parentNP=None): return self.getHpr(parentNP)[1]
    def getR(self, parentNP=None): return self.getHpr(parentNP)[2]

    def setHpr(self, h=None, p=None, r=None):
        if self.getAxis() == A_INTERNAL:
            hpr = self.__center.getHpr()
        else:
            hpr = self.getHpr()

        if h is None: h = hpr[0]
        if p is None: p = hpr[1]
        if r is None: r = hpr[2]

        h %= 360
        p %= 360
        r %= 360

        if self.getAxis() == A_INTERNAL:
            self.__nodes.wrtReparentTo(self.__center)
            self.__center.setHpr(h, p, r)
            self.__nodes.wrtReparentTo(self)
        else:
            NodePath.setHpr(self, h, p, r)

    def setH(self, h): self.setHpr(h=h)
    def setP(self, p): self.setHpr(p=p)
    def setR(self, r): self.setHpr(r=r)

    def getScale(self, parentNP=None):
        if parentNP is None: parentNP = self
        return self.__nodes.getScale(parentNP)

    def setScale(self, sX=None, sY=None, sZ=None):
        scale = self.__nodes.getScale()
        if sX is None: sX = scale[0]
        if sY is None: sY = scale[1]
        if sZ is None: sZ = scale[2]

        oldCP = self.getCenter()
        self.__nodes.setScale(sX, sY, sZ)

        if self.getAxis() == A_INTERNAL:
            newCP = self.getCenter()
            self.setPos(self.getPos() - (newCP - oldCP))
