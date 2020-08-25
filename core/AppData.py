from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from .TileSet import TileSet


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)


class AppData:

    def __init__(self):
        self.loader = None

    def load(self, f_path, f_opts):
        self.loader = TileSet(f_path, f_opts)
