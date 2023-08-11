#!/usr/local/bin/python3.9

import panda3d.core as p3d

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase


COLORS = [
    p3d.VBase4(0x00, 0x00, 0x00, 0xFF),
    p3d.VBase4(0x7F, 0x7F, 0x7F, 0xFF),
    p3d.VBase4(0xFF, 0xFF, 0xFF, 0xFF),
]


class SceneCellMaker(object):

    _cm = p3d.CardMaker('cell')
    _cm.set_frame(-0.5, 0.5, -0.5, 0.5)

    def __init__(self, parent: p3d.NodePath):
        super().__init__()
        self._parent = parent
        self._pool = []
        self._size = 0

    def __next__(self):
        np = self._parent.attach_new_node(self._cm.generate())
        self._pool.append(cell := SceneCell(self._size, np))
        self._size += 1

        cell.set_two_sided(True)
        cell.set_color(COLORS[self._size])
        cell.set_x(self._size)


class SceneCell(DirectObject):

    def __init__(self, index: int, node: p3d.NodePath):
        super().__init__()
        self._index = index
        self._node = node

    def __getattribute__(self, value: str):
        if value != '_node':
            return self._node.__getattribute__(value)
        else:
            return super().__getattribute__('_node')


class SceneEditor2D(ShowBase):

    def __init__(self):
        super().__init__()
        self._cell = SceneCellMaker(render)

    def run(self):
        smiley = loader.load_model('smiley.egg')
        smiley.reparent_to(render)
        smiley.set_pos(0, 5, 0)

        next(self._cell)
        next(self._cell)
        next(self._cell)

        super().run()


SceneEditor2D().run()
