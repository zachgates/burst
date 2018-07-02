import argparse

from panda3d.core import loadPrcFile, Filename
from panda3d.core import CardMaker, NodePath, TextureStage, TransparencyAttrib

from direct.interval.IntervalGlobal import Func, Sequence, Wait
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from src.common import FileManager
from src.visual.nodes import AngularNode


class TestApp(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)
        loadPrcFile('editor.prc')
        self._index = 0
        self._node = None

    def run(self):
        fileManager = FileManager(args.root)
        fileList = list(fileManager.loadDirectory('storage/tex'))

        self._textures = []
        while fileList:
            virtualPath = fileList.pop(0)
            fname = virtualPath.getBasenameWoExtension()

            if fname.endswith('_a'):
                self._textures.append((virtualPath, fileList.pop(0)))
            else:
                self._textures.append((virtualPath, None))

        taskMgr.doMethodLater(1, self.display, 'test')
        ShowBase.run(self)

    def display(self, task):
        if self._node:
            self._node.removeNode()

        texPath, alphaPath = self._textures[self._index]
        self._node = self.build(texPath, alphaPath)
        self._node.reparentTo(render2d)
        self._node.setPos(-0.5, 0, -0.5)
        print self._node.getName()

        self._index += 1
        self._index %= len(self._textures)
        return task.again

    def build(self, texPath, alphaPath):
        tex = loader.loadTexture(texPath, alphaPath)
        cm = CardMaker(texPath.getBasenameWoExtension())
        cm.setFrame(0, 1, 0, 1)
        frame = hidden.attachNewNode(cm.generate())
        frame.setTexture(tex)
        frame.setTransparency(TransparencyAttrib.MBinary)
        frame.setTwoSided(True)
        return AngularNode(frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default='./palettes')
    args = parser.parse_args()
    app = TestApp(args)
    app.run()
