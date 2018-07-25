from .. import nodes
from .SelectionManager import SelectionManager


class ObjectManager(SelectionManager):

    def acceptAll(self):
        SelectionManager.acceptAll(self)
        self.acceptPosAdjust()
        self.acceptHprAdjust()
        self.acceptScaleAdjust()

    def acceptPosAdjust(self):
        # event names
        upX = config.GetString('event-move-north', 'arrow_up')
        downX = config.GetString('event-move-south', 'arrow_down')
        upY = config.GetString('event-move-east', 'arrow_right')
        downY = config.GetString('event-move-west', 'arrow_left')
        # modifiers
        nVec = config.GetInt('position-mod', 5)
        pVec = config.GetInt('position-mod-precision', 1)
        # move up
        self.accept(upX, self.__adjustPos, [nVec, 0, 1])
        self.accept(upX + '-repeat', self.__adjustPos, [nVec, 0, 1])
        # move up with precision
        self.accept('shift-' + upX, self.__adjustPos, [pVec, 0, 1])
        self.accept('shift-%s-repeat' % upX, self.__adjustPos, [pVec, 0, 1])
        # move down
        self.accept(downX, self.__adjustPos, [nVec, 0, -1])
        self.accept(downX + '-repeat', self.__adjustPos, [nVec, 0, -1])
        # move down with precision
        self.accept('shift-' + downX, self.__adjustPos, [pVec, 0, -1])
        self.accept('shift-%s-repeat' % downX, self.__adjustPos, [pVec, 0, -1])
        # move left
        self.accept(downY, self.__adjustPos, [nVec, -1, 0])
        self.accept(downY + '-repeat', self.__adjustPos, [nVec, -1, 0])
        # move left with precision
        self.accept('shift-' + downY, self.__adjustPos, [pVec, -1, 0])
        self.accept('shift-%s-repeat' % downY, self.__adjustPos, [pVec, -1, 0])
        # move right
        self.accept(upY, self.__adjustPos, [nVec, 1, 0])
        self.accept(upY + '-repeat', self.__adjustPos, [nVec, 1, 0])
        # move right with precision
        self.accept('shift-' + upY, self.__adjustPos, [pVec, 1, 0])
        self.accept('shift-%s-repeat' % upY, self.__adjustPos, [pVec, 1, 0])

    def ignorePosAdjust(self):
        self.ignoreAll()
        self.acceptHprAdjust()

    def acceptHprAdjust(self):
        # event names
        cwEvent = config.GetString('event-rotate-clockwise', 'a')
        ccwEvent = config.GetString('event-rotate-counterclockwise', 'd')
        # modifiers
        nVec = config.GetInt('rotation-mod', 45)
        pVec = config.GetInt('rotation-mod-precision', 5)
        # rotate clockwise
        self.accept(cwEvent, self.__adjustHpr, [-nVec])
        self.accept(cwEvent + '-repeat', self.__adjustHpr, [nVec])
        # rotate clockwise with precision
        self.accept('shift-' + cwEvent, self.__adjustHpr, [-pVec])
        self.accept('shift-%s-repeat' % cwEvent, self.__adjustHpr, [-pVec])
        # rotate counter-clockwise
        self.accept(ccwEvent, self.__adjustHpr, [nVec])
        self.accept(ccwEvent + '-repeat', self.__adjustHpr, [nVec])
        # rotate counter-clockwise with precision
        self.accept('shift-' + ccwEvent, self.__adjustHpr, [pVec])
        self.accept('shift-%s-repeat' % ccwEvent, self.__adjustHpr, [pVec])

    def acceptScaleAdjust(self):
        # event names
        growEvent = config.GetString('event-scale-up', 'w')
        shrinkEvent = config.GetString('event-scale-down', 's')
        # modifiers
        nVec = config.GetFloat('scale-mod', 0.1)
        # increase scale
        self.accept(growEvent, self.__adjustScale, [nVec])
        self.accept(growEvent + '-repeat', self.__adjustScale, [nVec])
        # decrease scale
        self.accept(shrinkEvent, self.__adjustScale, [-nVec])
        self.accept(shrinkEvent + '-repeat', self.__adjustScale, [-nVec])

    def ignoreHprAdjust(self):
        self.ignoreAll()
        self.acceptPosAdjust()

    def __adjustPos(self, amount, x_dir, y_dir):
        curPos = self.getSelection().getPos()
        self.getSelection().setPos(curPos[0] + amount * x_dir,
                                   curPos[1] + amount * y_dir,
                                   curPos[2])

    def __adjustHpr(self, amount):
        curH = self.getSelection().getH()
        self.getSelection().setH(curH + amount)

    def __adjustScale(self, direction):
        sX, sY, sZ = self.getSelection().getScale()
        self.getSelection().setScale(round(sX + direction, 1),
                                     round(sY + direction, 1),
                                     round(sZ + direction, 1))
        self.getSelection()._readjustCenter()
