__all__ = [
    'Prop',
]


from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode

from burst.character import Collider, Sprite


class Prop(Sprite, Collider, DistributedNode):

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.set_transparency(p3d.TransparencyAttrib.MAlpha)

        scene = self.cr.scene_manager.get_scene()
        Sprite.__init__(self, cr, scene, 'sprite')
        self.reparent_to(self.scene.get_layer('prop'))

        Collider.__init__(self, cr, self.get_sx() * 0.5, 'none', 'char')
