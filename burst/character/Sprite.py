__all__ = [
    'Sprite',
    'SpriteData',
]


import dataclasses
import collections
import typing

from panda3d import core as p3d


class Sprite(p3d.SequenceNode):

    Track = collections.namedtuple('Track', 'name cells frame_rate')

    def __init__(self, scene, name: str):
        super().__init__(name)
        self.scene = scene
        self._blend = None
        self._tracks = {}
        # self._fsm = ...

    def add_track(self, track: Track):
        if track.frame_rate < 0:
            raise ValueError('bad track: expected frame_rate > 0')

        self._tracks[track.name] = (
            track,
            range(
                start := self.get_num_children(),
                start + len(track.cells) - 1,
                ))

        for cell in track.cells:
            np = self.scene.make_tile_card(row = cell[0], column = cell[1])
            self.add_child(np.node())

            if self._blend is not None:
                tile = np.node().get_python_tag('tile')
                tile.set_blend(self._blend)

    def get_tracks(self) -> list[Track]:
        return [track for track, rng in self._tracks]

    def set_tracks(self, tracks: typing.Iterable[Track]):
        for track in tracks:
            self.add_track(track)

    # AnimInterface

    def pose(self, name: str):
        track, rng = self._tracks[name]
        self.set_frame_rate(track.frame_rate)
        super().pose(rng.start)

    def play(self, name: str):
        track, rng = self._tracks[name]
        self.set_frame_rate(track.frame_rate)
        super().play(rng.start, rng.stop)

    def loop(self, name: str, restart: bool = True):
        track, rng = self._tracks[name]
        self.set_frame_rate(track.frame_rate)
        super().loop(restart, rng.start, rng.stop)

    def pingpong(self, name: str, restart: bool = True):
        track, rng = self._tracks[name]
        self.set_frame_rate(track.frame_rate)
        super().pingpong(restart, rng.start, rng.stop)

    # Tile

    def set_blend(self, blend: p3d.LColor):
        if isinstance(blend, p3d.LColor):
            self._blend = blend
            for index in range(self.get_num_children()):
                node = self.get_child(index)
                tile = node.get_python_tag('tile')
                tile.set_blend(self._blend)
        else:
            raise TypeError('expected LColor')

    def set_blend_off(self):
        for index in range(self.get_num_children()):
            node = self.get_child(index)
            tile = node.get_python_tag('tile')
            tile.set_blend_off(self._blend)

        self._blend = None


@dataclasses.dataclass
class SpriteData(object):

    name: str
    tracks: typing.Iterable[Sprite.Track]
    blend: p3d.LColor

    def __iter__(self):
        yield from dataclasses.astuple(self)
