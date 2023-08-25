__all__ = [
    'Prop',
]


from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode

from burst.character import Collider, SpriteData


class Prop(Collider, DistributedNode):

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.set_transparency(p3d.TransparencyAttrib.MAlpha)

        scene = base.cr.scene_manager.get_scene()
        self.reparent_to(scene.get_layer('prop'))

        factor = 4
        self.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        Collider.__init__(self, cr, self.get_sx() * 0.5, 'none', 'char')

        self._sprite_data = SpriteData('sprite', [], p3d.LColor())
        self._sprite = None

    ###

    def get_sprite(self) -> SpriteData:
        return self._sprite_data

    def set_sprite(self, data):
        scene = base.cr.scene_manager.get_scene()
        self._sprite_data = SpriteData(*data)
        self._sprite = scene.make_sprite(self._sprite_data)
        self.node().add_child(self._sprite)

    def d_set_sprite(self, data):
        self.sendUpdate('set_sprite', [data])

    def b_set_sprite(self, data):
        self.set_sprite(data)
        self.d_set_sprite(data)
