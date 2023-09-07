__all__ = [
    'Character',
]


import abc
import typing

from panda3d import core as p3d

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.task import Task

from burst.character import Collider, Mover, Responder, Sprite


class Character(Sprite, Collider, Responder, Mover, DistributedSmoothNode,
                metaclass = abc.ABCMeta,
                ):

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        self.set_transparency(p3d.TransparencyAttrib.MAlpha)

        scene = self.cr.scene_manager.get_scene()
        Sprite.__init__(self, cr, 'sprite')
        self.reparent_to(scene.get_layer('char'))

        Collider.__init__(self, cr, 'char', 'prop')
        Responder.__init__(self, cr)
        Mover.__init__(self, cr)

    def generate(self):
        super().generate()

        if self.cr.isLocalId(self.doId):
            base.cTrav.add_collider(self.get_cnodepath(), base.cEvent)
        self.get_cnode().set_radius(self.get_sx() * 0.5)

        self.set_bounds(
            p3d.Vec3((self.get_sx() - 1), 0, (self.get_sz() - 1)),
            p3d.Vec3(abs(self.get_sx() - 1), 0, abs(self.get_sz() - 1)),
            )

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
