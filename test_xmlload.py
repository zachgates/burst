from panda3d.core import CardMaker, TransparencyAttrib

from direct.showbase.ShowBase import ShowBase

from src import nodes
from src.control.FileManager import FileManager
from src.control.ObjectManager import ObjectManager


class TestApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.fileMgr = FileManager()
        self.fileMgr._fext = 'xml'
        self.objMgr = ObjectManager('pickable')

    def run(self):
        self.wall_tex = dict(self.loadWalls())
        self.street_pieces = dict(self.loadStreets())

        fobj = self.fileMgr.load('xml/toontown_central_2100.xml')
        self.street = render.attachNewNode(fobj.fname)

        for elem in fobj.tree.iterfind('.//flat_building'):
            self.placeWall(elem)

        for elem in fobj.tree.iterfind('.//street'):
            self.placeStreet(elem)

        base.mouseInterfaceNode.setPos(6.91992, 1174.64, 260.551)
        base.mouseInterfaceNode.setHpr(1.30776, 67.7645, -0.310472)

        ShowBase.run(self)

    def loadWalls(self):
        files = list(FileManager().load('palettes/storage/walls'))
        while files:
            fobj = files.pop(0)
            if fobj.fname.endswith('_a'):
                yield (fobj.fname[:-2], (fobj.fpath, files.pop(0).fpath))
            else:
                yield (fobj.fname, (fobj.fpath, None))

    def placeWall(self, elem):
        data = elem.attrib
        data.update(elem.find('pos').attrib)
        data.update(elem.find('nhpr').attrib)

        wall = elem.find('wall')
        if wall is None:
            return

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

        wall = render.attachNewNode(cm.generate())
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
        model = loader.loadModel('palettes/storage/streets.bam')
        for child in model.getChildren():
            yield (child.getName(), child)

    def placeStreet(self, elem):
        data = elem.attrib
        data.update(elem.find('pos').attrib)
        data.update(elem.find('nhpr').attrib)

        model = self.street_pieces.get(data['code'])
        if model:
            piece = nodes.AngularNode(self.street, np=model, mode=nodes.N_COPY)
        else:
            print data['code']
            return

        piece.setTag(self.objMgr.getNetTag(), 'true')
        piece.setPos(float(data['x']), float(data['y']), float(data['z']))
        piece.setHpr(float(data['h']), float(data['p']), float(data['r']))
        piece.setAxis(nodes.A_INTERNAL)

        texPaths = {
            'street_street_TT_tex': 'phase_3.5/maps/sidewalkbrown.jpg',
            'street_sidewalk_TT_tex': 'phase_3.5/maps/sidewalk_4cont_brown.jpg',
            'street_curb_TT_tex': 'phase_3.5/maps/curb_brown_even.jpg',
        }

        for i, e in enumerate(elem.iterfind('.//texture')):
            subNP = piece.find('**/*_%s' % e.text.split('_')[1])
            if subNP:
                tex = loader.loadTexture(texPaths.get(e.text))
                if tex:
                    subNP.setTexture(tex, 1)

        subNP = piece.find('**/*_grass')
        if subNP:
            tex = loader.loadTexture('phase_4/maps/grass.jpg')
            if tex:
                subNP.setTexture(tex, 1)


if __name__ == '__main__':
    app = TestApp()
    app.run()
