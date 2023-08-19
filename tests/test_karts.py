import math

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from burst.core import AngularNode

from .gui import make_label


SCALE_INTERVAL = 1.0 / 55
SCALE_FACTOR = 2.75


class KartDisplay(ShowBase):

    def __init__(self):
        super().__init__()
        self.label = make_label()
        self.label.setText('press the space bar')
        self.label.show()

        self._model = burst.store.load_file('data/models/kart.bam').read()
        self._model.set_h(90)

        self.karts = []
        for index in range(5):
            kart = AngularNode(parent = render, node = self._model)
            kart.set_y(index * 2.5)
            kart.set_python_tag('wheels', wheels := [])
            self.karts.append(kart)

            for node in kart.find_all_matches('**/wheelNode*'):
                wheel = AngularNode(
                    parent = node.get_parent(),
                    node = node,
                    mode = AngularNode.MODES.ORIGINAL,
                    )
                wheel.set_axis(AngularNode.AXES.INTERNAL)
                wheels.append(wheel)

        self.disable_mouse()
        self.camera.set_pos(30, -20, 25)
        self.camera.set_hpr(35, -40, 0)
        self.accept('space', self.toggle)

    @staticmethod
    def drive_task(kart: AngularNode, index: int, mph: int, task):
        for wheel in kart.get_python_tag('wheels'):
            dimensions = wheel.get_dimensions()
            circumference = dimensions.x * math.pi
            speed = (task.delay_time * mph) / circumference
            wheel.set_p(wheel.get_p() + (speed * 360))

        kart.set_x(kart.get_x() + (speed * circumference * SCALE_FACTOR))

        if task.time > SCALE_FACTOR:
            return task.done
        return task.cont

    def toggle(self):
        if self.label.is_hidden():
            self.label.show()
            self.task_mgr.removeTasksMatching('kart-*')
            for kart in self.karts:
                kart.set_x(0)
        else:
            self.label.hide()
            for index, kart in enumerate(self.karts):
                self.task_mgr.do_method_later(
                    SCALE_INTERVAL,
                    self.drive_task,
                    f'kart-{index}',
                    extraArgs = [kart, index, pow(2, index) / 5.0],
                    appendTask = True,
                    )


if __name__ == '__main__':
    app = KartDisplay()
    app.run()
