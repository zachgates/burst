import argparse

from . import constants
from .common import FileManager, load_xml_files

from direct.showbase.ShowBase import ShowBase


parser = argparse.ArgumentParser()
parser.add_argument('--root', type=str, default='./dna')
args = parser.parse_args()


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        base.fileManager = FileManager(args.root)
        for type_, files in load_xml_files().items():
            for fobj in files:
                print(fobj)


if __name__ == '__main__':
    app = TestApp()
    app.run()
