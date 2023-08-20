__all__ = [
    'SceneManager',
]


import burst

from panda3d import core as p3d

from direct.distributed.DistributedObject import DistributedObject


class SceneManager(DistributedObject):

    def __init__(self, cr):
        super().__init__(cr)
        self._file = None
        self._scene = None

    def generate(self):
        super().generate()
        base.scene_manager = self
        base.messenger.send('scene-manager-ready')

    def request(self, path: str, callback: callable):
        self.d_request(path)
        self.accept_once('set_scene', callback)

    def d_request(self, path: str):
        self.sendUpdate('request', [path])

    def set_scene(self, path: str, zone: int):
        self._file = burst.store.load_file(path)
        self._scene = self._file.read()
        base.cr.addInterest(zone)
        base.messenger.send('set_scene', [zone])

    def get_scene(self):
        return self._scene
