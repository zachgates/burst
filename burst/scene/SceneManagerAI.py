__all__ = [
    'SceneManagerAI',
]

import burst

from panda3d import core as p3d

from direct.distributed.DistributedObjectAI import DistributedObjectAI


class SceneManagerAI(DistributedObjectAI):

    def __init__(self, air):
        super().__init__(air)
        self._zone_id = 3
        self._zones = {}

    def get_next_zone(self):
        zone = self._zone_id
        self._zone_id += 1
        return zone

    def request(self, path):
        if (zone := self._zones.get(path)) is None:
            zone = self._zones[path] = self.get_next_zone()
            do = self.air.createDistributedObject(
                className = 'CharacterAI',
                zoneId = zone,
                )

        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(sender, 'set_scene', [path, zone])
