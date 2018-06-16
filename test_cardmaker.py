from panda3d.core import CardMaker, NodePath, TextureStage, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from src.visual.nodes import OrbitalNode


tex_uv_map = {
    'wall_lg_brick': (
        'phase_3.5/maps/phase_3.5_palette_3cmla_2',
        (0.0078125, 0.731069982051849),
        (0.484375, 0.23738002777099598),
        True,
    ),
    'wall_lg_rock': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.257813006639481, 0.757812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    'wall_md_blank': (
        'phase_3.5/maps/phase_3.5_palette_1lmla_1',
        (0.015625, 0.515625),
        (0.46875, 0.46875),
        True,
    ),
    'wall_md_board': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.257813006639481, 0.507812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    'wall_md_bricks': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.0078125, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    'wall_md_dental': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.507812976837158, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    'wall_md_pillars': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.0078125, 0.0078125),
        (0.484375, 0.234375),
        True,
    ),
    'wall_sm_brick_blue': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.757812976837158, 0.507812976837158),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_brick_pink': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.507812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_brick': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.757812976837158, 0.757812976837158),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_cement': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.757812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    'wall_sm_wood': (
        'phase_3.5/maps/walls_palette_3cmla_1',
        (0.0078125, 0.507812976837158),
        (0.234375, 0.484375),
        True,
    ),
    'wall_bricks': (
        'phase_3.5/maps/phase_3.5_palette_3cmla_2',
        (0.0552885010838509, 0.18359400331974),
        (0.2373799905180931, 0.234374985098839),
        True,
    ),
    'wall_stone_fence': (
        'phase_3.5/maps/fence_stoneWall',
        None,
        None,
        False,
    ),
    'wall_woodflower_fence': (
        'phase_3.5/maps/fenceW_flower',
        None,
        None,
        False,
    ),
    'wall_fence_wood': (
        'phase_3.5/maps/wall_fence_wood',
        None,
        None,
        False,
    ),
    'wall_sm_cement_blue': (
        'phase_3.5/maps/wall_sm_cement_blue',
        None,
        None,
        True,
    ),
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
        self._node = self.build(name, *tex_uv_map[name])
        self._node.reparentTo(render2d)
        self._node.setPos(-0.5, 0, -0.5)
        print self._node.getName()

        self._index += 1
        self._index %= len(tex_uv_map.keys())
        return task.again

    def build(self, name, tex, offset, scale, opaque):
        # Create the 2d plane
        cm = CardMaker(name)
        cm.setFrame(0, 1, 0, 1)
        # Create the card with the texture
        frame = hidden.attachNewNode(cm.generate())
        frame.setTwoSided(True)
        # Set the texture
        if opaque:
            texture = loader.loadTexture('%s.jpg' % tex)
        else:
            texture = loader.loadTexture(
                '%s.jpg' % tex,
                '%s_a.rgb' % tex)
        frame.setTexture(texture)
        # Account for transparency
        frame.setTransparency(TransparencyAttrib.MBinary)
        # Fit the texture to the plane
        if offset:
            frame.setTexOffset(TextureStage.getDefault(), *offset)
        if scale:
            frame.setTexScale(TextureStage.getDefault(), *scale)
        # Return our pivotal representation
        return OrbitalNode(frame)

    def buildFromCustom(self):
        n = self.build(
            'wall_sm_wood',
            'my_wall_palette',
            (0.0078125, 0.507812976837158),
            ((256 * 0.234375) / 384, 0.484375),
            True,
        )
        n.reparentTo(render2d)
        n.setPos(-0.5, 0, -0.5)


if __name__ == '__main__':
    app = TestApp()
    app.run()
