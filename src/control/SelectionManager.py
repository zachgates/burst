#!/usr/local/bin/python3.9

from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject

from ..nodes import A_INTERNAL, AngularNode


class SelectionManager(DirectObject):

    def __init__(self, tag: str = None):
        super().__init__(self)
        self._mgr_tag = str(tag)

        self.__c_ray = CollisionRay()
        self.__c_trav = CollisionTraverser('trav-%s' % self.tag)
        self.__c_handler = CollisionHandlerQueue()

        mask = GeomNode.get_default_collide_mask()
        self.__c_node = CollisionNode('mouse-%s' % self.tag)
        self.__c_node.set_from_collide_mask(mask)
        self.__c_node.add_solid(self.__c_ray)

        cam_node = base.camera.attachNewNode(self.__c_node)
        self.__c_trav.addCollider(cam_node, self.__c_handler)

        self.__selection = AngularNode(parent = render, name = 'selection')
        self.__selection.setAxis(A_INTERNAL)
        self.__selection.setColor(1, 0, 0)

    def get_group_name(self):
        return self._mgr_tag

    group = property(get_group_name)

    def get_selection(self):
        return self.__selection

    selection = property(get_selection)

    def accept_all(self):
        self.accept_selection_events()

    def accept_selection_events(self):
        self.accept('mouse1', self.__mouse_select)
        self.accept('shift-mouse1', self.__mouse_select, [True])
        self.accept('control-a', self.__select_all)
        self.accept('control-d', self.reset)
        self.accept('control-backspace', self.__delete_selection)

    def __select_all(self):
        self.reset()
        for node in render.find_all_matches('**/=' + self.group):
            self.select(node)

    def __delete_selection(self):
        for node in self.selection:
            node.remove_node()

    def __contains__(self, node: p3d.NodePath):
        if node:
            return node.getKey() in self.getSelection().getKeys()
        else:
            return False

    is_selected = __contains__

    def select(self, node: p3d.NodePath):
        return self.__selection.attach(node)

    def deselect(self, node: p3d.NodePath):
        return node.detach_node()

    def reset(self):
        for node in self.selection:
            pyNP = AngularNode.getPyObj(node)
            self.deselect(pyNP)

    def __mouse_select(self, append: bool = False):
        node = self.__get_node_at_mouse()
        if not node:
            if p3d.ConfigVariableBool('empty-click-reset', True):
                self.reset()
            return

        if append and self.is_selected(node):
            self.deselect(node)
        elif self.is_selected(node):
            pass
        else:
            self.select(node)

    def __get_node_at_mouse(self):
        if not base.mouse_watcher_node.has_mouse():
            return None

        mpos = base.mouse_watcher_node.get_mouse()
        self.__c_ray.set_from_lens(base.cam_node, mpos.get_x(), mpos.get_y())
        self.__c_trav.traverse(render)

        if self.__c_handler.get_num_entries() > 0:
            self.__c_handler.sort_entries()
            node = self.__c_handler.get_entry(0).get_into_node_path()
            node = node.findNetTag(self.group)
            node = AngularNode.getPyObj(node)
        else:
            node = None

        return node
