__all__ = [
    'Sprite',
]


import typing

from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject


class Sprite(DirectObject):

    def __init__(self, scene, blend = None):
        super().__init__()

        self.scene = scene
        self.node = p3d.SequenceNode('sprite')
        self.np = base.aspect2d.attach_new_node(self.node)
        self.np.set_transparency(p3d.TransparencyAttrib.MAlpha)

        self._blend = blend
        self._tracks = {}
        # self._fsm = ...

    def add_track(self, name: str, cells: typing.Iterable[tuple[int, int]]):
        track = self._tracks[name] = []
        for i, cell in enumerate(cells, start = self.node.get_num_children()):
            tex, np = self.scene.make_tile(row = cell[0], column = cell[1])
            tex.set_blend(self._blend)
            self.node.add_child(np.node())
            track.append(i)
