__all__ = [
    'Collider',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode


class _Collider(p3d.NodePath):

    MASKS = {
        'none': p3d.BitMask32.all_off(),
        'char': p3d.BitMask32(0x0F),
        'prop': p3d.BitMask32(0xF0),
    }

    def __init__(self,
                 np: p3d.NodePath,
                 radius: typing.Union[int, float],
                 from_mask: str,
                 into_mask: str,
                 ):
        super().__init__(p3d.CollisionNode(np.get_name()))
        self.node().set_from_collide_mask(_Collider.MASKS.get(from_mask))
        self.node().set_into_collide_mask(_Collider.MASKS.get(into_mask))
        self.node().add_solid(p3d.CollisionSphere(0, 0, 0, radius))
        self.set_python_tag('realnode', np)
        self.show()


class Collider(DistributedNode):

    def __init__(self,
                 cr,
                 radius: typing.Union[int, float],
                 from_mask: str = 'none',
                 into_mask: str = 'none',
                 ):
        super().__init__(cr)
        self._collider = _Collider(self, radius, from_mask, into_mask)
        self._collider.reparent_to(base._collisions)
        self._collider.set_pos(self.get_pos())

    def delete(self):
        self._collider.remove_node()
        super().delete()

    ### DistributedNode

    def set_x(self, x):
        super().set_x(x)
        self._collider.set_x(x)

    def set_y(self, y):
        super().set_y(y)
        self._collider.set_y(y)

    def set_z(self, z):
        super().set_z(z)
        self._collider.set_z(z)

    def set_pos(self, x, y, z):
        super().set_pos(x, y, z)
        self._collider.set_pos(x, y, z)

    def d_set_pos(self, x, y, z):
        self.sendUpdate('setPos', [x, y, z])

    def b_set_pos(self, x, y, z):
        self.set_pos(x, y, z)
        self.d_set_pos(x, y, z)

    ### DistributedSmoothNode

    def setComponentX(self, x):
        super().setComponentX(x)
        self._collider.set_x(x)

    def setComponentY(self, y):
        super().setComponentY(y)
        self._collider.set_y(y)

    def setComponentZ(self, z):
        super().setComponentZ(z)
        self._collider.set_z(z)
