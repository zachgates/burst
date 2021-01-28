__all__ = ['AngularNode']


import enum

from typing import Iterator

import panda3d.core as p3d

from direct.showbase.DirectObject import DirectObject


class AngularNode(DirectObject, p3d.NodePath):

    AXES = enum.IntEnum(
        'AXES', (
            'EXTERNAL',
            'INTERNAL',
            ), start = 0)

    MODES = enum.IntEnum(
        'MODES', (
            'ORIGINAL',
            'INSTANCE',
            'MAKECOPY',
            ), start = 0)

    @classmethod
    def get_class_tag(cls, node: p3d.NodePath):
        obj = node.get_python_tag(cls.__name__)
        return (obj if isinstance(obj, cls) else None)

    def __init__(self,
                 /, *,
                 parent: p3d.NodePath = None,
                 node: p3d.NodePath = None,
                 prefix: str = None,
                 mode: int = MODES.MAKECOPY,
                 ):
        DirectObject.__init__(self)
        p3d.NodePath.__init__(self,
                              ((prefix if prefix is not None
                                else f'{self.__class__.__name__}:')
                               +
                               (('empty' if node is None else node.get_name())
                                if node is not None else ''))
                              )

        self.set_python_tag(self.__class__.__name__, self)

        self.__axis = self.AXES.EXTERNAL
        self.__center = self.attach_new_node('center')
        self.__nodes = self.attach_new_node('nodes')
        self.__next_parent = hidden

        if parent is None:
            parent = hidden

        obj = self.get_class_tag(parent)
        if obj:
            obj.attach(self)
        else:
            self.reparent_to(parent)

        self.__next_parent = self.get_parent()

        if node is not None:
            if isinstance(node, self.__class__):
                self.attach(node.__nodes, mode)
                self.set_transform(node.get_transform())
            else:
                self.attach(node, mode)

    def __iter__(self) -> Iterator[p3d.NodePath]:
        for node in self.get_children():
            yield node

    # AngularNode helpers

    def get_dimensions(self) -> p3d.Point3:
        bounds = self.get_tight_bounds()
        if bounds:
            min_, max_ = self.get_tight_bounds()
            return max_ - min_
        else:
            return p3d.Point3.zero()

    def get_center(self) -> p3d.Point3:
        return self.__nodes.get_bounds().get_center()

    def get_tight_center(self) -> p3d.Point3:
        bounds = self.get_tight_bounds()
        if bounds:
            min_, max_ = bounds
            return min_ + (self.get_dimensions() / 2)
        else:
            return p3d.Point3.zero()

    def adjust_center(self) -> p3d.Point3:
        self.__center.set_pos(self.get_tight_center())

    def attach(self,
               node: p3d.NodePath,
               mode: int = MODES.ORIGINAL,
               ) -> p3d.NodePath:
        if mode == self.MODES.ORIGINAL:
            obj = self.get_class_tag(node)
            if obj:
                obj.__next_parent = obj.get_parent()
                node = obj
        elif mode == self.MODES.INSTANCE:
            node = node.instance_to(self.get_parent())
        elif mode == self.MODES.MAKECOPY:
            node = node.copy_to(self.get_parent())
        else:
            raise ValueError(f'invalid mode value: {mode}')

        node.wrt_reparent_to(self.__nodes)
        # self.adjust_center()
        return node

    # AngularNode getters

    def get_keys(self) -> set:
        return set(np.get_key() for np in self)

    def get_future_parent(self) -> p3d.NodePath:
        return self.__next_parent

    def get_axis(self) -> int:
        return self.__axis

    def get_transform(self, other: p3d.NodePath = None):
        if other is None:
            other = render

        return (self.get_axis(),
                # top level
                self.get_pos(other),
                self.get_hpr(other),
                self.get_scale(other),
                # bottom level
                self.__nodes.get_pos(),
                self.__nodes.get_hpr(),
                self.__nodes.get_scale())

    # AngularNode setters

    def set_axis(self, value: int):
        for name in self.AXES.__members__:
            if value == getattr(self.AXES, name):
                self.__axis = value
                self.adjust_center()
                break
        else:
            raise ValueError(f'invalid axis value: {value}')

    def set_transform(self,
                      axis: int = None,
                      top_pos: p3d.Vec3 = None,
                      top_hpr: p3d.Vec3 = None,
                      top_scale: p3d.Vec3 = None,
                      bot_pos: p3d.Vec3 = None,
                      bot_hpr: p3d.Vec3 = None,
                      bot_scale: p3d.Vec3 = None,
                      other: p3d.NodePath = None,
                      ):
        try:
            (axis,
             top_pos, top_hpr, top_scale,
             bot_pos, bot_hpr, bot_scale) = axis
        except:
            pass

        if other is None: other = render
        if axis: self.set_axis(axis)
        if top_pos: self.set_pos(*top_pos)
        if top_hpr: self.set_hpr(*top_hpr)
        if top_scale: self.set_scale(*top_scale)
        if bot_pos: self.__nodes.set_pos(*bot_pos)
        if bot_hpr: self.__nodes.set_hpr(*bot_hpr)
        if bot_scale: self.__nodes.set_scale(*bot_scale)

    # NodePath overloads

    def get_children(self) -> list:
        return self.__nodes.get_children()

    def detach_node(self) -> p3d.NodePath:
        self.wrt_reparent_to(self.get_future_parent())
        self.__next_parent = hidden

        if obj := self.get_class_tag(self.get_parent()):
            obj.adjust_center()

        return self

    def copy_to(self, node: p3d.NodePath):
        return self.__nodes.copy_to(node)

    def instance_to(self, node: p3d.NodePath):
        return self.__nodes.instance_to(node)

    def remove_node(self):
        self.clear_python_tag(self.__class__.__name__)
        p3d.NodePath.remove_node(self)

    def get_h(self, other: p3d.NodePath = None):
        return self.get_hpr(other)[0]

    def get_p(self, other: p3d.NodePath = None):
        return self.get_hpr(other)[1]

    def get_r(self, other: p3d.NodePath = None):
        return self.get_hpr(other)[2]

    def get_hpr(self, other: p3d.NodePath = None):
        if other is None:
            other = self

        if self.get_axis() == self.AXES.INTERNAL:
            return self.__center.get_hpr(other)
        else:
            return self.__nodes.get_hpr(other)

    def set_h(self, value: float):
        self.set_hpr(h = value)

    def set_p(self, value: float):
        self.set_hpr(p = value)

    def set_r(self, value: float):
        self.set_hpr(r = value)

    def set_hpr(self, h: float = None, p: float = None, r: float = None):
        if self.get_axis() is self.AXES.INTERNAL:
            hpr = self.__center.get_hpr()
        else:
            hpr = self.get_hpr()

        if h is None:
            h = hpr[0]
        h %= 360

        if p is None:
            p = hpr[1]
        p %= 360

        if r is None:
            r = hpr[2]
        r %= 360

        if self.get_axis() is self.AXES.INTERNAL:
            self.__nodes.wrt_reparent_to(self.__center)
            self.__center.set_hpr(h, p, r)
            self.__nodes.wrt_reparent_to(self)
        else:
            p3d.NodePath.set_hpr(self, h, p, r)

    def get_sx(self, other: p3d.NodePath = None):
        return self.get_scale(other)[0]

    def get_sy(self, other: p3d.NodePath = None):
        return self.get_scale(other)[1]

    def get_sz(self, other: p3d.NodePath = None):
        return self.get_scale(other)[2]

    def get_scale(self, other: p3d.NodePath = None):
        if other is None:
            other = self

        return self.__nodes.get_scale(other)

    def set_sx(self, value: float):
        self.set_scale(sx = value)

    def set_sy(self, value: float):
        self.set_scale(sy = value)

    def set_sz(self, value: float):
        self.set_scale(sz = value)

    def set_scale(self, sx: float = None, sy: float = None, sz: float = None):
        scale = self.__nodes.get_scale()

        if sx is None:
            sx = scale[0]

        if sy is None:
            sy = scale[1]

        if sz is None:
            sz = scale[2]

        old = self.get_center()
        self.__nodes.set_scale(sX, sY, sZ)

        if self.get_axis() == self.AXES.INTERNAL:
            new = self.get_center()
            self.set_pos(self.get_pos() - (new - old))
