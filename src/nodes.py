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
    def getPyObj(cls, np):
        pyNP = np.getPythonTag(cls.__name__)
        return (pyNP if isinstance(pyNP, cls) else None)

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

        pyParentNP = self.getPyObj(parentNP)
        if pyParentNP:
            pyParentNP.attach(self)
        else:
            self.reparentTo(parentNP)

        self.__nextParent = self.getParent()
        if np is not None:
            self.attach(np, mode)

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
            np = self.getPyObj(np)
            if np:
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

    def getTransform(self, otherNP=None):
        if otherNP is None: otherNP = render
        return (self.getAxis(),
                # top level
                self.getPos(otherNP),
                self.getHpr(otherNP),
                self.getScale(otherNP),
                # bottom level
                self.__nodes.getPos(),
                self.__nodes.getHpr(),
                self.__nodes.getScale())

    # AngularNode setters

    def setAxis(self, code):
        if code == A_EXTERNAL or code == A_INTERNAL:
            self.__axis = code
            self._readjustCenter()
        else:
            self.notify.error('got invalid axis: %i' % code)

    def setTransform(self,
                     axis=None,
                     topPos=None, topRot=None, topScale=None,
                     botPos=None, botRot=None, botScale=None,
                     otherNP=None):
        try:
            axis, topPos, topRot, topScale, botPos, botRot, botScale = axis
        except TypeError:
            self.notify.error('invalid transform')
            return

        if otherNP is None: otherNP = render
        if axis: self.setAxis(axis)
        if topPos: self.setPos(otherNP, topPos)
        if topRot: self.setHpr(otherNP, topRot)
        if topScale: self.setScale(otherNP, topScale)
        if botPos: self.__nodes.setPos(botPos)
        if botRot: self.__nodes.setPos(botRot)
        if botScale: self.__nodes.setScale(botScale)

    # NodePath overloads

    def detachNode(self):
        pyParentNP = self.getPyObj(self.getParent())
        self.wrtReparentTo(self.getFutureParent())
        self.__nextParent = hidden

        if pyParentNP:
            pyParentNP._readjustCenter()

        return self

    def copyTo(self, parentNP):
        return self.__nodes.copyTo(parentNP)

    def instanceTo(self, parentNP):
        return self.__nodes.instanceTo(parentNP)

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        NodePath.removeNode(self)

    def getH(self, otherNP=None): return self.getHpr(otherNP)[0]
    def getP(self, otherNP=None): return self.getHpr(otherNP)[1]
    def getR(self, otherNP=None): return self.getHpr(otherNP)[2]

    def getHpr(self, otherNP=None):
        if otherNP is None: otherNP = self
        if self.getAxis() == A_INTERNAL:
            return self.__center.getHpr(otherNP)
        else:
            return self.__nodes.getHpr(otherNP)

    def setH(self, h): self.setHpr(h=h)
    def setP(self, p): self.setHpr(p=p)
    def setR(self, r): self.setHpr(r=r)

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

    def getSx(self, otherNP=None): return self.getScale(otherNP)[0]
    def getSy(self, otherNP=None): return self.getScale(otherNP)[1]
    def getSz(self, otherNP=None): return self.getScale(otherNP)[2]

    def getScale(self, otherNP=None):
        if otherNP is None: otherNP = self
        return self.__nodes.getScale(otherNP)

    def setSx(self, sX): self.setScale(sX=sX)
    def setSy(self, sY): self.setScale(sY=sY)
    def setSz(self, sZ): self.setScale(sZ=sZ)

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
