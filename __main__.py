import argparse

from . import constants
from .common import FileManager

from direct.showbase.ShowBase import ShowBase


class TestApp(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)
        self.fileManager = FileManager(args.root)

    def run(self):
        for type_, files in self.load_xml_files().items():
            for fobj in files:
                print(fobj)

        ShowBase.run(self)

    def load_xml_files(self):
        files = []
        types = set()

        for virtualFile in vfs.scanDirectory(self.fileManager.ROOT):
            xml = base.fileManager.loadXML(virtualFile)
            if xml:
                files.append(xml)
                types.add(xml.name)

        return {type_: [fobj for fobj in files if fobj.name == type_]
                for type_ in types}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default='./dna')
    args = parser.parse_args()
    app = TestApp(args)
    app.run()
