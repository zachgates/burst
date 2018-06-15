from panda3d.core import NodePath, CardMaker, TextureStage, TransparencyAttrib
from direct.showbase.ShowBase import ShowBase

from src.visual.nodes import PivotNode2D


tex_uv = (
    (
        'wall_lg_brick',
        'phase_3.5_palette_3cmla_2',
        (0.0078125, 0.731069982051849),
        (0.484375, 0.23738002777099598),
        True,
    ),
    (
        'wall_lg_rock',
        'walls_palette_3cmla_1',
        (0.257813006639481, 0.757812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    (
        'wall_md_blank',
        'phase_3.5_palette_1lmla_1',
        (0.015625, 0.515625),
        (0.46875, 0.46875),
        True,
    ),
    (
        'wall_md_board',
        'walls_palette_3cmla_1',
        (0.257813006639481, 0.507812976837158),
        (0.484374970197677, 0.234375),
        True,
    ),
    (
        'wall_md_bricks',
        'walls_palette_3cmla_1',
        (0.0078125, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    (
        'wall_md_dental',
        'walls_palette_3cmla_1',
        (0.507812976837158, 0.257813006639481),
        (0.484375, 0.234375),
        True,
    ),
    (
        'wall_md_pillars',
        'walls_palette_3cmla_1',
        (0.0078125, 0.0078125),
        (0.484375, 0.234375),
        True,
    ),
    (
        'wall_sm_brick_blue',
        'walls_palette_3cmla_1',
        (0.757812976837158, 0.507812976837158),
        (0.234375, 0.234375),
        True,
    ),
    (
        'wall_sm_brick_pink',
        'walls_palette_3cmla_1',
        (0.507812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    (
        'wall_sm_brick',
        'walls_palette_3cmla_1',
        (0.757812976837158, 0.757812976837158),
        (0.234375, 0.234375),
        True,
    ),
    (
        'wall_sm_cement',
        'walls_palette_3cmla_1',
        (0.757812976837158, 0.0078125),
        (0.234375, 0.234375),
        True,
    ),
    (
        'wall_sm_wood',
        'walls_palette_3cmla_1',
        (0.0078125, 0.507812976837158),
        (0.234375, 0.484375),
        True,
    ),
    (
        'wall_bricks',
        'phase_3.5_palette_3cmla_2',
        (0.0552885010838509, 0.18359400331974),
        (0.2373799905180931, 0.234374985098839),
        True,
    ),
    (
        'wall_sm_cement_blue',
        'wall_sm_cement_blue',
        None,
        None,
        True,
    ),
    (
        'wall_stone_fence',
        'fence_stoneWall',
        None,
        None,
        False,
    ),
    (
        'wall_woodflower_fence',
        'fenceW_flower',
        None,
        None,
        False,
    ),
    (
        'wall_fence_wood',
        'wall_fence_wood',
        None,
        None,
        False,
    ),
)


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self._index = 0
        self._node = None

    def run(self):
        taskMgr.doMethodLater(2, self.buildNode, 'test')
        ShowBase.run(self)

    def build(self, name, tex, offset, scale, opaque):
        # Create the 2d plane
        cm = CardMaker('wall_lg_brick')
        cm.setFrame(0, 1, 0, 1)
        # Create the card with the texture
        frame = hidden.attachNewNode(cm.generate())
        # Set the texture
        if opaque:
            texture = loader.loadTexture('phase_3.5/maps/%s.jpg' % tex)
        else:
            texture = loader.loadTexture(
                'phase_3.5/maps/%s.jpg' % tex,
                'phase_3.5/maps/%s_a.rgb' % tex)
        frame.setTexture(texture)
        # Account for transparency
        frame.setTransparency(TransparencyAttrib.MBinary)
        # Fit the texture to the plane
        if offset:
            frame.setTexOffset(TextureStage.getDefault(), *offset)
        if scale:
            frame.setTexScale(TextureStage.getDefault(), *scale)
        # Return our pivotal representation
        return PivotNode2D(frame)

    def buildNode(self, task):
        if self._node:
            self._node.removeNode()

        self._node = self.build(*tex_uv[self._index])
        self._node.reparentTo(render)

        self._index += 1
        self._index %= len(tex_uv)
        return task.again


if __name__ == '__main__':
    app = TestApp()
    app.run()
