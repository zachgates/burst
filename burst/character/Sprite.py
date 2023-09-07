__all__ = [
    'Sprite',
]


import dataclasses
import collections
import typing

from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode


class Sprite(DistributedNode):

    Track = collections.namedtuple('Track', 'name cells frame_rate')

    def __init__(self, cr, name: str):
        DistributedNode.__init__(self, cr)
        self.node().add_child(p3d.SequenceNode(name))

        self._blend = p3d.LColor.zero()
        self._tracks = {}
        self._tilesheet = 0

    def _get_seq_node(self):
        return self.node().get_child(0)

    def generate(self):
        super().generate()
        scene = self.cr.scene_manager.get_scene()
        factor = 4
        self.set_scale(p3d.Vec3(
            (self.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (self.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

    @property
    def tiles(self):
        scene = self.cr.scene_manager.get_scene()
        return scene.tiles(self.get_tilesheet())

    def get_tilesheet(self) -> int:
        return self._tilesheet

    def set_tilesheet(self, index: int):
        self._tilesheet = index

    def d_set_tilesheet(self, index: int):
        self.sendUpdate('set_tilesheet', [index])

    def b_set_tilesheet(self, index: int):
        self.set_tilesheet(index)
        self.d_set_tilesheet(index)

    def get_tracks(self) -> list[Track]:
        return [tuple(track) for name, (track, rng) in self._tracks.items()]

    def set_tracks(self, tracks):
        for track in tracks:
            self.add_track(Sprite.Track(*track))

    def d_set_tracks(self, tracks):
        self.sendUpdate('set_tracks', tracks)

    def b_set_tracks(self, tracks):
        self.set_tracks(tracks)
        self.d_set_tracks([self.get_tracks()])

    def add_track(self, track: Track):
        if track.frame_rate < 0:
            raise ValueError('bad track: expected frame_rate > 0')

        self._tracks[track.name] = (
            track,
            range(
                start := self._get_seq_node().get_num_children(),
                start + len(track.cells) - 1,
                ))

        for row, column in track.cells:
            np = self.tiles.make_tile_card(row = row, column = column)
            self._get_seq_node().add_child(np.node())

            if self._blend is not None:
                tile = np.node().get_python_tag('tile')
                tile.set_blend(self._blend)

    # Tile

    def get_blend(self) -> p3d.LColor:
        return self._blend

    def set_blend(self, blend: typing.Iterable[int]):
        if isinstance(blend, typing.Iterable) and (len(blend) == 4):
            self._blend = p3d.LColor(*blend)
            for index in range(self._get_seq_node().get_num_children()):
                node = self._get_seq_node().get_child(index)
                tile = node.get_python_tag('tile')
                tile.set_blend(self._blend)
        else:
            raise TypeError('expected uint8[4]')

    def d_set_blend(self, blend: typing.Iterable[int]):
        self.sendUpdate('set_blend', [blend])

    def b_set_blend(self, blend: typing.Iterable[int]):
        self.set_blend(blend)
        self.d_set_blend(blend)

    def set_blend_off(self):
        for index in range(self.node().get_num_children()):
            node = self.node().get_child(index)
            tile = node.get_python_tag('tile')
            tile.set_blend_off(self._blend)

        self._blend = p3d.LColor.zero()

    # SequenceNode

    def pose(self, name: str):
        track, rng = self._tracks[name]
        self._get_seq_node().set_frame_rate(track.frame_rate)
        self._get_seq_node().pose(rng.start)

    def play(self, name: str):
        track, rng = self._tracks[name]
        self._get_seq_node().set_frame_rate(track.frame_rate)
        self._get_seq_node().play(rng.start, rng.stop)

    def loop(self, name: str, restart: bool = True):
        track, rng = self._tracks[name]
        self._get_seq_node().set_frame_rate(track.frame_rate)
        self._get_seq_node().loop(restart, rng.start, rng.stop)

    def pingpong(self, name: str, restart: bool = True):
        track, rng = self._tracks[name]
        self._get_seq_node().set_frame_rate(track.frame_rate)
        self._get_seq_node().pingpong(restart, rng.start, rng.stop)

    def is_playing(self):
        return self._get_seq_node().is_playing()
