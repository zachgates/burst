__all__ = [
    'Mover',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode
from direct.task import Task


class Mover(DistributedNode):

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self._bounds = (p3d.Vec3(-1, 0, -1), p3d.Vec3(1, 0, 1))
        self._speed_factor = 1.0

    ###

    def get_bounds(self) -> tuple[p3d.Vec3, p3d.Vec3]:
        return self._bounds

    def set_bounds(self, min_: p3d.Vec3, max_: p3d.Vec3):
        self._bounds = (min_, max_)

    bounds = property(get_bounds, set_bounds)

    ###

    def get_speed_factor(self) -> float:
        return self._speed_factor

    def set_speed_factor(self, value: typing.Union[int, float]):
        self._speed_factor = float(value)

    speed_factor = property(get_speed_factor, set_speed_factor)

    ###

    def set_x(self, x):
        self.set_pos(x, self.get_y(), self.get_z())

    def set_y(self, y):
        self.set_pos(self.get_x(), y, self.get_z())

    def set_z(self, z):
        self.set_pos(self.get_x(), self.get_y(), z)

    def set_pos(self, x, y, z):
        super().set_pos(
            min(max(x, self._bounds[0].get_x()), self._bounds[1].get_x()),
            min(max(y, self._bounds[0].get_y()), self._bounds[1].get_y()),
            min(max(z, self._bounds[0].get_z()), self._bounds[1].get_z()),
            )

    ###

    def __get_input_vector(self) -> p3d.Vec3:
        return p3d.Vec3(
            x = ((base.mouseWatcherNode.is_button_down('arrow_right')
                  - base.mouseWatcherNode.is_button_down('arrow_left')
                  ) * self.get_sx()),
            y = 0,
            z = ((base.mouseWatcherNode.is_button_down('arrow_up')
                  - base.mouseWatcherNode.is_button_down('arrow_down')
                  ) * self.get_sz()),
            )

    def _watch(self, hook = (lambda *a, **kw: None)):
        if is_moving := any(vector := self.__get_input_vector()):
            pos = self.get_pos() + (vector * self.get_speed_factor())
            self.set_pos(*pos)

        hook(is_moving)
        return Task.again
