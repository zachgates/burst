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
        self._zone = 0

    def generate(self):
        super().generate()
        print(f'SceneManager({self.doId}).generate')
        base.cr.scene_manager = self
        base.messenger.send('scene-manager-ready')

    def request(self, path: str, callback: callable):
        self.d_request(path)
        self.accept_once('set_scene', callback)

    def d_request(self, path: str):
        self.sendUpdate('request', [path])

    def set_scene(self, path: str, zone: int):
        print(f'SceneManager({self.doId}).set_scene {zone}')
        self._file = burst.store.load_file(path)
        self._scene = self._file.read()
        self._zone = zone
        base.cr.addInterestZone(zone)
        base.messenger.send('set_scene')

    def get_scene(self):
        return self._scene

    def get_zone(self):
        return self._zone
