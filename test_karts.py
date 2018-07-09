import math
import uuid

from direct.showbase.ShowBase import ShowBase

from src import nodes


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

    def run(self):
        m = loader.loadModel('wheel.bam')

        wheel_one = nodes.AngularNode(m)
        wheel_one.reparentTo(render)
        wheel_one.setAxis(nodes.A_INTERNAL)

        wheel_two = wheel_one.copyTo(render)
        wheel_two.setZ(-1)

        wheel_three = wheel_two.copyTo(render)
        wheel_three.setZ(-2)

        wheel_four = wheel_three.copyTo(render)
        wheel_four.setZ(-3)

        self.setup(wheel_one, 1)
        self.setup(wheel_two, 2)
        self.setup(wheel_three, 4)
        self.setup(wheel_four, 8)

        ShowBase.run(self)

    def setup(self, np, mph):
        np.accept('space', lambda: self.taskMgr.doMethodLater(
            0.01, self.roll, uuid.uuid4().hex,
            extraArgs=[np, mph], appendTask=True))

    def roll(self, np, mph, task):
        if task.frame == 0:
            def pause():
                taskMgr.remove(task.name)
                np.accept('space', lambda: self.taskMgr.doMethodLater(
                    0.01, self.roll, task.name,
                    extraArgs=[np, mph], appendTask=True))
            np.accept('space', pause)

        diameter = np.getDimensions()[0]
        circumference = diameter * math.pi
        speed = (task.delayTime * mph) / circumference
        np.setX(np.getX() + (speed * circumference))
        np.getNode().setR(np.getNode().getR() + (speed * 360))
        return task.again


if __name__ == '__main__':
    app = TestApp()
    app.run()
