from panda3d.core import CardMaker, TransparencyAttrib

from direct.showbase.ShowBase import ShowBase

from src.control.FileManager import FileManager
from src.nodes import AngularNode


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self._index = 0
        self._node = None
        self._textures = []

        files = list(FileManager().load('palettes/storage/walls'))
        while files:
            virtualFile = files.pop(0)
            if virtualFile.fname.endswith('_a'):
                self._textures.append((virtualFile, files.pop(0).fpath))
            else:
                self._textures.append((virtualFile, None))

    def run(self):

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
        tex = loader.loadTexture(texPath.fpath, alphaPath)
        cm = CardMaker(texPath.fname)
        cm.setFrame(0, 1, 0, 1)
        frame = hidden.attachNewNode(cm.generate())
        frame.setTexture(tex)
        frame.setTransparency(TransparencyAttrib.MBinary)
        frame.setTwoSided(True)
        return AngularNode(frame)


if __name__ == '__main__':
    app = TestApp()
    app.run()
