__all__ = [
    'Collider',
]


import typing

from panda3d import core as p3d


class Collider(p3d.NodePath):

    MASKS = {
        'none': p3d.BitMask32.all_off(),
        'char': p3d.BitMask32(0x0F),
        'prop': p3d.BitMask32(0xF0),
    }

    def __init__(self,
                 np: p3d.NodePath,
                 radius: typing.Union[int, float],
                 from_mask: str = 'none',
                 into_mask: str = 'none',
                 ):

        super().__init__(p3d.CollisionNode(np.get_name()))
        self.node().set_from_collide_mask(Collider.MASKS.get(from_mask))
        self.node().set_into_collide_mask(Collider.MASKS.get(into_mask))
        self.node().add_solid(p3d.CollisionSphere(0, 0, 0, radius))
        self.set_python_tag('realnode', np)
        self.show()
