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
        self._chars = {}

    def get_next_zone(self):
        zone = self._zone_id
        self._zone_id += 1
        return zone

    def request(self, path):
        sender = self.air.getAvatarIdFromSender()
        print(f'SceneManagerAI request {sender}')

        if (zone := self._zones.get(path)) is None:
            zone = self._zones[path] = self.get_next_zone()
        #     self._chars.setdefault(zone, {})
        # else:
        #     for char in self._chars[zone].values():
        #         # self.air.sendDeleteMsg(char.doId)
        #         char.sendUpdate('set_active', [False])
        #
        # char = self._chars[zone][sender] = self.air.createDistributedObject(
        #     className = 'CharacterAI',
        #     zoneId = zone,
        #     )

        print('sendUpdate', sender, 'set_scene', path, zone)
        self.sendUpdateToAvatarId(sender, 'set_scene', [path, zone])
        # char.sendUpdate('set_active', [True])
