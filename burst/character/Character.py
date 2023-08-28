__all__ = [
    'Character',
]


import abc
import typing

from panda3d import core as p3d

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.task import Task

from burst.character import Collider, Mover, Responder, Sprite, SpriteData


class Character(Collider, Responder, Mover, DistributedSmoothNode,
                metaclass = abc.ABCMeta,
                ):

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        self.set_transparency(p3d.TransparencyAttrib.MAlpha)

        scene = self.cr.scene_manager.get_scene()
        self.reparent_to(scene.get_layer('char'))
        factor = 4
        self.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        self._sprite_data = SpriteData('sprite', [], p3d.LColor.zero())
        self._sprite = None

        Collider.__init__(self, cr, (self.get_sx() * 0.5), 'char', 'prop')
        Responder.__init__(self, cr)
        Mover.__init__(self, cr)
        self.set_bounds(
            p3d.Vec3((self.get_sx() - 1), 0, (self.get_sz() - 1)),
            p3d.Vec3(abs(self.get_sx() - 1), 0, abs(self.get_sz() - 1)),
            )

    ###

    def get_sprite(self) -> SpriteData:
        return self._sprite_data

    def set_sprite(self, data):
        print(f'Character({self.doId}).set_sprite')
        print(data)

        if self._sprite:
            print('remove_child')
            self.node().remove_child(self._sprite)

        scene = self.cr.scene_manager.get_scene()
        self._sprite_data = SpriteData(*data)
        self._sprite = scene.make_sprite(self._sprite_data)
        self.node().add_child(self._sprite)
        print('add_child')

    def d_set_sprite(self, data):
        self.sendUpdate('set_sprite', [data])

    def b_set_sprite(self, data):
        self.set_sprite(data)
        self.d_set_sprite(data)

    ###

    def _watch(self):
        Mover._watch(self, self.set_moving)
        Responder._watch(self, self.b_set_action)
        return Task.again

    @abc.abstractmethod
    def set_moving(self, is_moving: bool):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_action(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def set_action(self, action: str):
        raise NotImplementedError()

    def d_set_action(self, action: str):
        self.sendUpdate('set_action', [action])

    def b_set_action(self, action: str):
        self.set_action(action)
        self.d_set_action(action)
