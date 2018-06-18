import argparse
import re

from panda3d.core import loadPrcFile, ConfigVariableString

from direct.showbase.ShowBase import ShowBase

from src.common import FileManager


MODEL_EXT = ConfigVariableString('default-model-extension')


class TestApp(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)
        loadPrcFile('./editor.prc')
        self.fileManager = FileManager(args.root)

    def run(self):
        print dict(self.loadPalettes())

    def loadPalettes(self, relpath='./palettes'):
        self.fileManager.setRestrictToExt('')

        for virtualPath in self.fileManager.loadDirectory(relpath, foldersOnly=True):
            paletteGroups = dict(self.loadPaletteGroups(virtualPath))
            yield (virtualPath.getBasename(), paletteGroups)

    def loadPaletteGroups(self, virtualPath):
        self.fileManager.setRestrictToExt(MODEL_EXT)
        dir_ = self.fileManager.loadDirectory(str(virtualPath), filesOnly=True)

        for fname in dir_:
            model = loader.loadModel(fname.getFullpathWoExtension())
            yield (fname.getBasenameWoExtension(), model.getChildren())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default='.')
    args = parser.parse_args()
    app = TestApp(args)
    app.run()
