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
        Sprite.__init__(self, cr, 'sprite')
        self.reparent_to(scene.get_layer('prop'))

        Collider.__init__(self, cr, 'none', 'char')

    def generate(self):
        super().generate()
        self.get_cnode().set_radius(self.get_sx() * 0.5)
