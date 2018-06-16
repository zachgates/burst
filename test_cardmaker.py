from panda3d.core import CardMaker, NodePath, TextureStage, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from src.visual.nodes import OrbitalNode


tex_uv_map = {
##    'wall_lg_brick': (
##        'phase_3.5/maps/phase_3.5_palette_3cmla_2',
##        (0.0078125, 0.731069982051849),
##        (0.484375, 0.23738002777099598),
##        True,
##    ),
##    'wall_md_blank': (
##        'phase_3.5/maps/phase_3.5_palette_1lmla_1',
##        (0.015625, 0.515625),
##        (0.46875, 0.46875),
##        True,
##    ),
    'wall_lg_rock': (
        (0.257813006639481, 0.757812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    'wall_md_board': (
        (0.257813006639481, 0.507812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    'wall_md_brick': (
        (0.0078125, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    'wall_md_dental': (
        (0.507812976837158, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    'wall_md_pillars': (
        (0.0078125, 0.0078125),
        (0.484375, 0.234375),
        True,
    ),
    'wall_sm_brick_blue': (
        (0.757812976837158, 0.507812976837158),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_brick_pink': (
        (0.507812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_brick': (
        (0.757812976837158, 0.757812976837158),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_cement': (
        (0.757812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_wood': (
        (0.0078125, 0.507812976837158),
        (0.234375, 0.484375),
        True,
    ),
##    'wall_bricks': (
##        'phase_3.5/maps/phase_3.5_palette_3cmla_2',
##        (0.0552885010838509, 0.18359400331974),
##        (0.2373799905180931, 0.234374985098839),
##        True,
##    ),
##    'wall_stone_fence': (
##        'phase_3.5/maps/fence_stoneWall',
##        None,
##        None,
##        False,
##    ),
##    'wall_woodflower_fence': (
##        'phase_3.5/maps/fenceW_flower',
##        None,
##        None,
##        False,
##    ),
##    'wall_fence_wood': (
##        'phase_3.5/maps/wall_fence_wood',
##        None,
##        None,
##        False,
##    ),
##    'wall_sm_cement_blue': (
##        'phase_3.5/maps/wall_sm_cement_blue',
##        None,
##        None,
##        True,
##    ),
}


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self._index = 0
        self._node = None

    def run(self):
        taskMgr.doMethodLater(1, self.display, 'test')
        ShowBase.run(self)

    def display(self, task):
        if self._node:
            self._node.removeNode()

        name = tex_uv_map.keys()[self._index]
        self._node = self.build(name)
        self._node.reparentTo(render2d)
        self._node.setPos(-0.5, 0, -0.5)
##        print self._node.getName()

        self._index += 1
        self._index %= len(tex_uv_map.keys())
        return task.again

    def build(self, name):
        offset, scale, opaque = tex_uv_map[name]

        if opaque:
            tex = loader.loadTexture('palettes/storage/tex/%s.jpg' % name)
        else:
            tex = loader.loadTexture('palettes/storage/tex/%s.jpg' % name,
                                     'palettes/storage/tex/%s_a.rgb' % name)

        cm = CardMaker(name)
        cm.setFrame(0, 1, 0, 1)

        frame = hidden.attachNewNode(cm.generate())
        frame.setTexture(tex)
        frame.setTransparency(TransparencyAttrib.MBinary)
        frame.setTwoSided(True)

        return OrbitalNode(frame)


if __name__ == '__main__':
    app = TestApp()
    app.run()
