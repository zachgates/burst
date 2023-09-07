__all__ = [
    'Collider',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedNode import DistributedNode


class _Collider(p3d.CollisionNode):

    MASKS = {
        'none': p3d.BitMask32.all_off(),
        'char': p3d.BitMask32(0x0F),
        'prop': p3d.BitMask32(0xF0),
    }

    def __init__(self,
                 name: str,
                 from_mask: str,
                 into_mask: str,
                 ):
        super().__init__(name)
        self._sphere = p3d.CollisionSphere(0, 0, 0, 1)
        self.set_from_collide_mask(_Collider.MASKS.get(from_mask))
        self.set_into_collide_mask(_Collider.MASKS.get(into_mask))
        self.add_solid(self._sphere)

    def get_radius(self):
        return self._sphere.get_radius()

    def set_radius(self, radius):
        self._sphere.set_radius(radius)

    radius = property(get_radius, set_radius)


class Collider(DistributedNode):

    def __init__(self,
                 cr,
                 from_mask: str = 'none',
                 into_mask: str = 'none',
                 ):
        DistributedNode.__init__(self, cr)
        self.__cnode = _Collider(self.get_name(), from_mask, into_mask)
        self.__cnodepath = base._collisions.attach_new_node(self.__cnode)
        self.__cnodepath.set_pos(self.get_pos())
        self.__cnodepath.set_python_tag('realnode', self)
        self.__cnodepath.show()

    def delete(self):
        self.__cnodepath.remove_node()
        super().delete()

    def get_cnode(self):
        return self.__cnode

    def get_cnodepath(self):
        return self.__cnodepath

    ### DistributedNode

    def set_x(self, x):
        super().set_x(x)
        self.get_cnodepath().set_x(x)

    def set_y(self, y):
        super().set_y(y)
        self.get_cnodepath().set_y(y)

    def set_z(self, z):
        super().set_z(z)
        self.get_cnodepath().set_z(z)

    def set_pos(self, x, y, z):
        super().set_pos(x, y, z)
        self.get_cnodepath().set_pos(x, y, z)

    def d_set_pos(self, x, y, z):
        self.sendUpdate('setPos', [x, y, z])

    def b_set_pos(self, x, y, z):
        self.set_pos(x, y, z)
        self.d_set_pos(x, y, z)

    ### DistributedSmoothNode

    def setComponentX(self, x):
        super().setComponentX(x)
        self.get_cnodepath().set_x(x)

    def setComponentY(self, y):
        super().setComponentY(y)
        self.get_cnodepath().set_y(y)

    def setComponentZ(self, z):
        super().setComponentZ(z)
        self.get_cnodepath().set_z(z)
