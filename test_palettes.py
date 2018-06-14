import argparse
import re

from panda3d.core import loadPrcFile

from direct.showbase.ShowBase import ShowBase

from src.common import FileManager


class TestApp(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)
        loadPrcFile('./editor.prc')
        self.fileManager = FileManager(args.root)

    def run(self):
        print dict(self.loadPalettes())

    def loadPalettes(self, relpath='./palettes'):
        for virtualPath in self.fileManager.scan(relpath):
            paletteName = virtualPath.getFilename().getBasenameWoExtension()
            paletteGroups = dict(self.loadPaletteGroups(virtualPath))
            yield (paletteName, paletteGroups)

    def loadPaletteGroups(self, virtualPath):
        dir_ = self.fileManager.loadDirectory(virtualPath, modelsOnly=True)
        for fname in dir_:
            model = loader.loadModel(fname.getFullpathWoExtension())
            yield (fname.getBasenameWoExtension(), model.getChildren())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default='.')
    args = parser.parse_args()
    app = TestApp(args)
    app.run()
