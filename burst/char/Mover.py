__all__ = [
    'Mover',
]


import typing

from panda3d import core as p3d


class Mover(object):

    def __init__(self, np: p3d.NodePath, move_event: str):
        super().__init__()
        self._np = np
        self._bounds = (p3d.Vec3(-1, 0, -1), p3d.Vec3(1, 0, 1))
        self._speed_factor = 1.0
        self._task = None
        self.__move_event = move_event

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

    def start(self, frame_rate: int):
        self._task = base.task_mgr.do_method_later(
            (1 / frame_rate),
            self._move, f'{self._move!r}',
            appendTask = True,
            )

    def stop(self):
        base.task_mgr.remove(self._task)

    ###

    def _move(self, task):
        if moving := any(vector := self.__get_input_vector()):
            pos = self._np.get_pos() + (vector * self.get_speed_factor())

            if pos.get_x() < self._bounds[0].get_x():
                pos.set_x(self._bounds[0].get_x())
            if pos.get_z() < self._bounds[0].get_z():
                pos.set_z(self._bounds[0].get_z())

            if pos.get_x() > self._bounds[1].get_x():
                pos.set_x(self._bounds[1].get_x())
            if pos.get_z() > self._bounds[1].get_z():
                pos.set_z(self._bounds[1].get_z())

            self._np.set_pos(pos)

        base.messenger.send(self.__move_event, [moving])
        return task.again

    def __get_input_vector(self) -> p3d.Vec3:
        return p3d.Vec3(
            x = ((base.mouseWatcherNode.is_button_down('arrow_right')
                  - base.mouseWatcherNode.is_button_down('arrow_left')
                  ) * self._np.get_sx()),
            y = 0,
            z = ((base.mouseWatcherNode.is_button_down('arrow_up')
                  - base.mouseWatcherNode.is_button_down('arrow_down')
                  ) * self._np.get_sz()),
            )
