from panda3d.core import CardMaker, TransparencyAttrib

from direct.showbase.ShowBase import ShowBase

from src import nodes
from src.control import FileManager, SelectionManager


class TestApp(ShowBase, SelectionManager):

    def __init__(self):
        ShowBase.__init__(self)
        SelectionManager.__init__(self, 'pickable')

        self.fileMgr = FileManager()
        self.fileMgr._fext = 'xml'

    def select(self, np):
        SelectionManager.select(self, np)
        if np:
            np.setColor(1, 0, 0)

    def deselect(self, np):
        SelectionManager.deselect(self, np)
        if np:
            np.setColor(1, 1, 1)

    def run(self):
        self.wall_tex = self.loadWalls()
        self.street_pieces = self.loadStreets()

        fobj = self.fileMgr.load('xml/toontown_central_2200.xml')
        self.street = render.attachNewNode(fobj.fname)

        for elem in fobj.tree.iterfind('.//flat_building'):
            self.placeWall(elem)

        for elem in fobj.tree.iterfind('.//street'):
            self.placeStreet(elem)

        ShowBase.run(self)

    def loadWalls(self):
        files = list(FileManager().load('palettes/storage/walls'))
        walls = {}

        while files:
            fobj = files.pop(0)
            if fobj.fname.endswith('_a'):
                walls[fobj.fname[:-2]] = (fobj.fpath, files.pop(0).fpath)
            else:
                walls[fobj.fname] = (fobj.fpath, None)

        return walls

    def placeWall(self, elem):
        data = elem.attrib
        data.update(elem.find('pos').attrib)
        data.update(elem.find('nhpr').attrib)

        wall = elem.find('wall')
        data.update(wall.attrib)
        data.update(wall.find('color').attrib)

        wall_code = data['code'].rsplit('_', 1)[0]
        if wall_code not in self.wall_tex:
            print wall_code
            return
        texPath, alphaPath = self.wall_tex.get(wall_code)
        tex = loader.loadTexture(texPath, alphaPath)

        cm = CardMaker(data['id'])
        cm.setFrame(0, 1, 0, 1)

        wall = self.street.attachNewNode(cm.generate())
        wall.setTexture(tex)
        wall.setTransparency(TransparencyAttrib.MBinary)
        wall.setTwoSided(True)

        wall.setPos(float(data['x']), float(data['y']), float(data['z']))
        wall.setHpr(float(data['h']), float(data['p']), float(data['r']))
        wall.setScale(float(data['width']), 1, float(data['height']))
        wall.setColor(float(data['r']),
                      float(data['g']),
                      float(data['b']),
                      float(data['a']))

    def loadStreets(self):
        models = loader.loadModel('palettes/storage/streets.bam')
        pieces = {}
        for child in models.getChildren():
            pieces[child.getName()] = child
        return pieces

    def placeStreet(self, elem):
        data = elem.attrib
        data.update(elem.find('pos').attrib)
        data.update(elem.find('nhpr').attrib)

        model = self.street_pieces.get(data['code'])
        if model:
            piece = nodes.AngularNode(model, mode=nodes.N_COPY)
            piece.reparentTo(self.street)
            piece.setTag('pickable', 'true')
            piece.setPos(float(data['x']), float(data['y']), float(data['z']))
            piece.setHpr(float(data['h']), float(data['p']), float(data['r']))
        else:
            print data['code']


if __name__ == '__main__':
    app = TestApp()
    app.run()
