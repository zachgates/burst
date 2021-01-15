from panda3d import core as p3d


PALETTES = {
    'TT': {
        'street': 'phase_3.5/maps/sidewalkbrown.jpg',
        'sidewalk': 'phase_3.5/maps/sidewalk_4cont_brown.jpg',
        'curb': 'phase_3.5/maps/curb_brown_even.jpg',
    },
    'DD': {
        'street': 'phase_3.5/maps/boardwalk_floor.jpg',
        'sidewalk': 'phase_3.5/maps/boardwalk_floor_dark.jpg',
        'curb': 'phase_3.5/maps/curb_boardwalk.jpg',
    },
    'MM': {
        'street': 'phase_3.5/maps/cobblestone_pink.jpg',
        'sidewalk': 'phase_3.5/maps/sidewalk_4cont_red.jpg',
        'curb': 'phase_3.5/maps/curb_red_even.jpg',
        'keyboard': 'phase_3.5/maps/keyboard_segment.jpg',
    },
    'BR': {
        'street': 'phase_3.5/maps/cobblestone_blue.jpg',
        'sidewalk': 'phase_3.5/maps/snow.jpg',
        'curb': 'phase_3.5/maps/snow.jpg',
        'grass': 'phase_3.5/maps/snow.jpg',
    },
    'DG': {
        'street': 'phase_3.5/maps/dustroad.jpg',
        'sidewalk': 'phase_3.5/maps/grassDG.jpg',
        'curb': 'phase_3.5/maps/grassDG.jpg',
    },
    'DL': {
        'street': 'phase_3.5/maps/cobblestone_purple.jpg',
        'sidewalk': 'phase_3.5/maps/sidewalk_4cont_purple.jpg',
        'curb': 'phase_3.5/maps/curb_purple_even.jpg',
    },
    'GS': {
        'street': 'phase_6/maps/speedway_asphaultA2.jpg',
        'sidewalk': 'phase_3.5/maps/grassTT.jpg',
        'curb': 'phase_6/maps/GoofyStadium_curb2.jpg',
    }
}


class group(p3d.NodePath):

    def __init__(self, parentNP, **kwargs):
        self.__kwargs = kwargs
        super().__init__(self.get('code'))
        self.reparentTo(parentNP)

    def get(self, key, default=None):
        return self.__kwargs.get(key, default)


class visgroup(group):

    def getPalette(self, code):
        for code, path in PALETTES.get(code, {}).items():
            yield (code, loader.loadTexture(path))

    def setPalette(self, code):
        for code, tex in self.getPalette(code):
            for np in self.findAllMatches('=palatable/' + code):
                np.setTexture(tex, 1)

    def rotatePalettes(self, task):
        if not hasattr(self, 'palette'):
            self.palette = -1
        keys = sorted(PALETTES)
        self.palette += 1
        self.palette %= len(keys)
        self.setPalette(keys[self.palette])
        return task.again


class street(group):

    model = loader.loadModel('new_streets.bam')

    def place(self):
        np = self.model.find('**/' + self.name)
        np = np.copyTo(hidden)
        self.node().stealChildren(np.node())
        self.setPosHpr(*(float(self.get(k, 0)) for k in 'xyzhpr'))
        self.setTag('palatable', 'true')
