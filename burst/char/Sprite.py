__all__ = [
    'Sprite',
]


import typing

from panda3d import core as p3d


class Sprite(p3d.SequenceNode):

    def __init__(self, scene, name: str, blend = None):
        super().__init__(name)
        self.scene = scene
        self._blend = blend
        self._tracks = {}
        # self._fsm = ...

    def add_track(self,
                  name: str,
                  cells: typing.Iterable[tuple[int, int]],
                  /, *,
                  frame_rate: int = 1,
                  ):

        if frame_rate < 0:
            raise ValueError('expected frame_rate > 0')

        start = self.get_num_children()
        self._tracks[name] = (frame_rate, range(start, start + len(cells)))

        for cell in cells:
            np = self.scene.get_tile_card(row = cell[0], column = cell[1])
            np.get_python_tag('tile').set_blend(self._blend)
            self.add_child(np.node())

    def play(self, name: str):
        rate, rng = self._tracks[name]
        self.set_frame_rate(rate)
        super().play(rng.start, rng.stop)

    def loop(self, name: str, restart: bool = True):
        rate, rng = self._tracks[name]
        self.set_frame_rate(rate)
        super().loop(restart, rng.start, rng.stop)

    def pingpong(self, name: str, restart: bool = True):
        rate, rng = self._tracks[name]
        self.set_frame_rate(rate)
        super().pingpong(restart, rng.start, rng.stop)
