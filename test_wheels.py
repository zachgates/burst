#!/usr/local/bin/python3.9

import math

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from src.nodes import A_INTERNAL, AngularNode


class WheelDisplay(ShowBase):

    def makeScene(self):
        wheel_model = loader.loadModel('wheel.bam')

        for index in range(5):
            wheel = AngularNode(parent = render, node = wheel_model)
            wheel.setAxis(A_INTERNAL)
            wheel.setZ(-index)
            wheel.acceptOnce(
                'space',
                self.moveWheel,
                extraArgs = [wheel, index],
                )

        wheel_model.reparentTo(render)
        wheel_model.setZ(1)

        self.camera.setPos(5, -20, -1)
        self.disableMouse()

    def moveWheel(self, wheel: AngularNode, index: int):
        def move(task):
            dimensions = wheel.getDimensions()
            circumference = dimensions.x * math.pi
            speed = (task.delayTime * pow(2, index)) / circumference
            wheel.setX(wheel.getX() + (speed * circumference))
            wheel.setR(wheel.getR() + (speed * 360))
            return task.again

        self.taskMgr.doMethodLater(0.01, move, f'wheel-{index}')


if __name__ == '__main__':
    app = WheelDisplay()
    app.makeScene()
    app.run()
