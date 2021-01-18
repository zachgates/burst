#!/usr/local/bin/python3.9

import math

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

import tests


SCALE_INTERVAL = 1.0 / 55
SCALE_FACTOR = 2.75


class KartDisplay(ShowBase):

    def make_scene(self):
        kart_model = loader.load_model('kart.bam')
        kart_model.set_h(90)

        for index in range(5):
            kart = self.make_kart(kart_model)
            kart.set_y(index * 2.5)
            kart.accept_once(
                'space',
                self.move_kart,
                extraArgs = [kart, index],
                )

        self.camera.set_pos(25, -20, 30)
        self.camera.set_hpr(30, -45, 0)
        self.disable_mouse()

    def make_kart(self, model: p3d.NodePath) -> burst.core.AngularNode:
        kart = burst.core.AngularNode(parent = render, node = model)
        wheels = []

        for node in kart.find_all_matches('**/wheelNode*'):
            wheel = burst.core.AngularNode(
                parent = node.get_parent(),
                node = node,
                mode = burst.core.AngularNode.MODES.ORIGINAL,
                )
            wheel.set_axis(burst.core.AngularNode.AXES.INTERNAL)
            wheels.append(wheel)

        kart.set_python_tag('wheels', wheels)
        return kart

    def move_kart(self, kart: burst.core.AngularNode, index: int):
        def drive_chain(mph, task):
            for wheel in kart.get_python_tag('wheels'):
                dimensions = wheel.get_dimensions()
                circumference = dimensions.x * math.pi
                speed = (task.delay_time * mph) / circumference
                wheel.set_p(wheel.get_p() + (speed * 360))

            kart.set_x(kart.get_x() + (speed * circumference * SCALE_FACTOR))
            return task.again

        self.task_mgr.do_method_later(
            SCALE_INTERVAL,
            drive_chain,
            f'drive_chain-{index}',
            extraArgs = [pow(2, index) / 5.0],
            appendTask = True,
            )


if __name__ == '__main__':
    app = KartDisplay()
    app.make_scene()
    app.run()
