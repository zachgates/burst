#!/usr/local/bin/python3.9

import math

from panda3d import core as p3d

from direct.showbase.ShowBase import ShowBase

from src.nodes import AngularNode


class WheelDisplay(ShowBase):

    def make_scene(self):
        wheel_model = loader.load_model('wheel.bam')

        for index in range(5):
            wheel = AngularNode(parent = render, node = wheel_model)
            wheel.set_axis(AngularNode.AXES.INTERNAL)
            wheel.set_z(-index)
            wheel.accept_once(
                'space',
                self.move_wheel,
                extraArgs = [wheel, index],
                )

        wheel_model.reparent_to(render)
        wheel_model.set_z(1)
        self.camera.set_pos(5, -20, -1)
        self.disable_mouse()

    def move_wheel(self, wheel: AngularNode, index: int):
        def move(task):
            dimensions = wheel.get_dimensions()
            circumference = dimensions.x * math.pi
            speed = (task.delay_time * pow(2, index)) / circumference
            wheel.set_x(wheel.get_x() + (speed * circumference))
            wheel.set_r(wheel.get_r() + (speed * 360))
            return task.again

        self.task_mgr.do_method_later(0.01, move, f'wheel-{index}')


if __name__ == '__main__':
    app = WheelDisplay()
    app.make_scene()
    app.run()
