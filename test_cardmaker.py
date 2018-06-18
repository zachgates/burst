from panda3d.core import CardMaker, NodePath, TextureStage, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from src.visual.nodes import OrbitalNode


tex_uv_map = {
    'wall_lg_brick': True,
    'wall_md_blank': True,
    'wall_lg_rock': True,
    'wall_md_board': True,
    'wall_md_brick': True,
    'wall_md_dental': True,
    'wall_md_pillars': True,
    'wall_sm_brick_blue': True,
    'wall_sm_brick_pink': True,
    'wall_sm_brick': True,
    'wall_sm_cement': True,
    'wall_sm_wood': True,
    'wall_bricks': True,
    'wall_stone_fence': False,
    'wall_woodflower_fence': False,
    'wall_fence_wood': False,
    'wall_sm_cement_blue': True,
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
        pathWoExt = 'palettes/storage/tex/%s' % name

        if tex_uv_map[name]:
            tex = loader.loadTexture(pathWoExt + '.jpg')
        else:
            tex = loader.loadTexture(pathWoExt + '.jpg', pathWoExt + '.rgb')

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
