#!/usr/local/bin/python3.9

import math

from direct.showbase.ShowBase import ShowBase

from src import nodes


SCALE_INTERVAL = 1.0 / 55
SCALE_FACTOR = 2.75


class KartDisplay(ShowBase):

    def makeScene(self):
        kart_model = loader.loadModel('kart.bam')
        kart_model.setH(90)

        for index in range(5):
            kart = self.makeKart(kart_model)
            kart.setY(index * 2.5)
            kart.acceptOnce('space', self.moveKart, extraArgs = [kart, index])

        self.camera.setPos(25, -20, 30)
        self.camera.setHpr(30, -45, 0)
        self.disableMouse()

    def makeKart(self, model):
        kart = nodes.AngularNode(render, model)
        wheels = []

        for np in kart.findAllMatches('**/wheelNode*'):
            wheel = nodes.AngularNode(np.getParent(), np, mode = nodes.N_ORIG)
            wheel.setAxis(nodes.A_INTERNAL)
            wheels.append(wheel)

        kart.setPythonTag('wheels', wheels)
        return kart

    def moveKart(self, kart, index):
        def drive(mph, task):
            for wheel in kart.getPythonTag('wheels'):
                dimensions = wheel.getDimensions()
                circumference = dimensions.x * math.pi
                speed = (task.delayTime * mph) / circumference
                wheel.setP(wheel.getP() + (speed * 360))

            kart.setX(kart.getX() + (speed * circumference * SCALE_FACTOR))
            return task.again

        self.taskMgr.doMethodLater(
            SCALE_INTERVAL,
            drive,
            f'drive-{index}',
            extraArgs = [pow(2, index) / 5.0],
            appendTask = True,
            )


if __name__ == '__main__':
    app = KartDisplay()
    app.makeScene()
    app.run()
