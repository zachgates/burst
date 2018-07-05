from direct.showbase.ShowBase import ShowBase

from src.base import FileManager


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.fileMgr = FileManager()
        self.fileMgr._fext = 'xml'

    def run(self):
        pass

    def testFolder(self):
        for e in self.fileMgr.load('xml'):
            print e.fname

    def testFile(self):
        fobj = self.fileMgr.load('xml/toontown_central_2100.xml')
        for elem in fobj.tree.iterfind('.//flat_building'):
            if elem is not None:
                print elem.attrib['id']


if __name__ == '__main__':
    app = TestApp()
    app.run()
