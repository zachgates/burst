#!/usr/local/bin/python3.9


from typing import Iterator

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal
from direct.showbase.DirectObject import DirectObject


A_EXTERNAL = 0
A_INTERNAL = 1

N_ORIG = 0
N_INST = 1
N_COPY = 2


class AngularNode(DirectObject, p3d.NodePath):

    notify = DirectNotifyGlobal.directNotify.newCategory('AngularNode')

    @classmethod
    def getPyObj(cls, node: p3d.NodePath):
        obj = node.getPythonTag(cls.__name__)
        return (obj if isinstance(obj, cls) else None)

    def __init__(self,
                 /, *,
                 parent: p3d.NodePath = None,
                 node: p3d.NodePath = None,
                 prefix: str = None,
                 mode: int = N_COPY,
                 ):
        DirectObject.__init__(self)
        p3d.NodePath.__init__(self,
                              ((prefix if prefix is not None
                                else f'{self.__class__.__name__}:')
                               +
                               (('empty' if node is None else node.getName())
                                if node is not None else ''))
                              )

        self.setPythonTag(self.__class__.__name__, self)

        self.__axis = A_EXTERNAL
        self.__center = self.attachNewNode('center')
        self.__nodes = self.attachNewNode('nodes')
        self.__nextParent = hidden

        if parent is None:
            parent = hidden

        obj = self.getPyObj(parent)
        if obj:
            obj.attach(self)
        else:
            self.reparentTo(parent)

        self.__nextParent = self.getParent()

        if node is not None:
            if isinstance(node, self.__class__):
                self.attach(node.__nodes, mode)
                self.setTransform(node.getTransform())
            else:
                self.attach(node, mode)

    def __iter__(self) -> Iterator:
        for np in self.getChildren():
            yield np

    # AngularNode helpers

    def getDimensions(self) -> p3d.Point3:
        bounds = self.getTightBounds()
        if bounds:
            min_, max_ = self.getTightBounds()
            return max_ - min_
        else:
            return p3d.Point3.zero()

    def getCenter(self) -> p3d.Point3:
        return self.__nodes.getBounds().getCenter()

    def getTightCenter(self) -> p3d.Point3:
        bounds = self.getTightBounds()
        if bounds:
            min_, max_ = bounds
            return min_ + (self.getDimensions() / 2)
        else:
            return p3d.Point3.zero()

    def _readjustCenter(self) -> p3d.Point3:
        self.__center.setPos(self.getCenter())

    def attach(self, node: p3d.NodePath, mode: int = N_ORIG):
        if mode == N_ORIG:
            obj = self.getPyObj(node)
            if obj:
                obj.__nextParent = obj.getParent()
                node = obj
        elif mode == N_INST:
            node = node.instanceTo(self.getParent())
        elif mode == N_COPY:
            node = node.copyTo(self.getParent())
        else:
            self.notify.error('got invalid mode: %i' % mode)
            return

        node.wrtReparentTo(self.__nodes)
        self._readjustCenter()
        return node

    # AngularNode getters

    def getKeys(self) -> set:
        return set(np.getKey() for np in self)

    def getFutureParent(self) -> p3d.NodePath:
        return self.__nextParent

    def getAxis(self) -> int:
        return self.__axis

    def getTransform(self, other: p3d.NodePath = None):
        if other is None:
            other = render

        return (self.getAxis(),
                # top level
                self.getPos(other),
                self.getHpr(other),
                self.getScale(other),
                # bottom level
                self.__nodes.getPos(),
                self.__nodes.getHpr(),
                self.__nodes.getScale())

    # AngularNode setters

    def setAxis(self, value: int):
        if value == A_EXTERNAL or value == A_INTERNAL:
            self.__axis = value
            self._readjustCenter()
        else:
            self.notify.error(f'got invalid axis: {value}')

    def setTransform(self,
                     axis: int = None,
                     topPos: p3d.Vec3 = None,
                     topHpr: p3d.Vec3 = None,
                     topScale: p3d.Vec3 = None,
                     botPos: p3d.Vec3 = None,
                     botHpr: p3d.Vec3 = None,
                     botScale: p3d.Vec3 = None,
                     other: p3d.NodePath = None,
                     ):
        try:
            axis, topPos, topHpr, topScale, botPos, botHpr, botScale = axis
        except:
            pass

        if other is None: other = render
        if axis: self.setAxis(axis)
        if topPos: self.setPos(*topPos)
        if topHpr: self.setHpr(*topHpr)
        if topScale: self.setScale(*topScale)
        if botPos: self.__nodes.setPos(*botPos)
        if botHpr: self.__nodes.setHpr(*botHpr)
        if botScale: self.__nodes.setScale(*botScale)

    # NodePath overloads

    def getChildren(self) -> list:
        return self.__nodes.getChildren()

    def detachNode(self) -> p3d.NodePath:
        self.wrtReparentTo(self.getFutureParent())
        self.__nextParent = hidden

        if obj := self.getPyObj(self.getParent()):
            obj._readjustCenter()

        return self

    def copyTo(self, node: p3d.NodePath):
        return self.__nodes.copyTo(node)

    def instanceTo(self, node: p3d.NodePath):
        return self.__nodes.instanceTo(node)

    def removeNode(self):
        self.clearPythonTag(self.__class__.__name__)
        p3d.NodePath.removeNode(self)

    def getH(self, other: p3d.NodePath = None):
        return self.getHpr(other)[0]

    def getP(self, other: p3d.NodePath = None):
        return self.getHpr(other)[1]

    def getR(self, other: p3d.NodePath = None):
        return self.getHpr(other)[2]

    def getHpr(self, other: p3d.NodePath = None):
        if other is None:
            other = self

        if self.getAxis() == A_INTERNAL:
            return self.__center.getHpr(other)
        else:
            return self.__nodes.getHpr(other)

    def setH(self, value: float):
        self.setHpr(h = value)

    def setP(self, value: float):
        self.setHpr(p = value)

    def setR(self, value: float):
        self.setHpr(r = value)

    def setHpr(self, h: float = None, p: float = None, r: float = None):
        if self.getAxis() == A_INTERNAL:
            hpr = self.__center.getHpr()
        else:
            hpr = self.getHpr()

        if h is None:
            h = hpr[0]
        h %= 360

        if p is None:
            p = hpr[1]
        p %= 360

        if r is None:
            r = hpr[2]
        r %= 360

        if self.getAxis() == A_INTERNAL:
            self.__nodes.wrtReparentTo(self.__center)
            self.__center.setHpr(h, p, r)
            self.__nodes.wrtReparentTo(self)
        else:
            p3d.NodePath.setHpr(self, h, p, r)

    def getSx(self, other: p3d.NodePath = None):
        return self.getScale(other)[0]

    def getSy(self, other: p3d.NodePath = None):
        return self.getScale(other)[1]

    def getSz(self, other: p3d.NodePath = None):
        return self.getScale(other)[2]

    def getScale(self, other: p3d.NodePath = None):
        if other is None:
            other = self

        return self.__nodes.getScale(other)

    def setSx(self, value: float):
        self.setScale(sX = value)

    def setSy(self, value: float):
        self.setScale(sY = value)

    def setSz(self, value: float):
        self.setScale(sZ = value)

    def setScale(self, sX: float = None, sY: float = None, sZ: float = None):
        scale = self.__nodes.getScale()

        if sX is None:
            sX = scale[0]

        if sY is None:
            sY = scale[1]

        if sZ is None:
            sZ = scale[2]

        old = self.getCenter()
        self.__nodes.setScale(sX, sY, sZ)

        if self.getAxis() == A_INTERNAL:
            new = self.getCenter()
            self.setPos(self.getPos() - (new - old))
