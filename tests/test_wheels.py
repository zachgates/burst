#!/usr/local/bin/python3

import math

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.core import AngularNode
from . import make_label


class WheelDisplay(ShowBase):

    def __init__(self):
        super().__init__()
        self.label = make_label()
        self.label.setText('press the space bar')
        self.label.show()

        self.wheels = []
        self._model = loader.load_model('tests/data/models/wheel.bam')
        self._model.reparent_to(render)
        self._model.set_z(1)

        for index in range(5):
            wheel = AngularNode(parent = render, node = self._model)
            wheel.set_axis(AngularNode.AXES.INTERNAL)
            wheel.set_z(-(index + 1))
            self.wheels.append(wheel)

        self.disable_mouse()
        self.camera.set_pos(5, -20, -1)
        self.accept('space', self.toggle)

    @staticmethod
    def roll_task(wheel: AngularNode, index: int, task):
        dimensions = wheel.get_dimensions()
        circumference = dimensions.x * math.pi
        speed = (task.delay_time * pow(2, index)) / circumference
        wheel.set_x(wheel.get_x() + (speed * circumference))
        wheel.set_r(wheel.get_r() + (speed * 360))

        if task.time > 1:
            return task.done
        return task.cont

    def toggle(self):
        if self.label.is_hidden():
            self.label.show()
            self.task_mgr.removeTasksMatching('wheel-*')
            for wheel in self.wheels:
                wheel.set_x(0)
                wheel.set_r(0)
        else:
            self.label.hide()
            for index, wheel in enumerate(self.wheels):
                self.task_mgr.do_method_later(
                    0.01,
                    self.roll_task,
                    f'wheel-{index}',
                    extraArgs = [wheel, index],
                    appendTask = True,
                    )

if __name__ == '__main__':
    app = WheelDisplay()
    app.run()
