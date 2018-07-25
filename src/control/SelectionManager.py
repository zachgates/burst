import uuid

from panda3d.core import *

from direct.showbase.DirectObject import DirectObject

from .. import nodes


class SelectionManager(DirectObject):

    def __init__(self, tag=None):
        DirectObject.__init__(self)
        self.__tag = str(tag) or uuid.uuid4().hex

        self.__coll_trav = CollisionTraverser('trav-%s' % self.getNetTag())
        self.__coll_handler = CollisionHandlerQueue()

        self.__selected = nodes.AngularNode(render, 'selection')
        self.__selected.setAxis(nodes.A_INTERNAL)
        self.__selected.setColor(1, 0, 0)

        self.__selector_ray = CollisionRay()
        self.__selector_node = CollisionNode('mouse-%s' % self.getNetTag())
        self.__selector_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.__selector_node.addSolid(self.__selector_ray)

        np = camera.attachNewNode(self.__selector_node)
        self.__coll_trav.addCollider(np, self.__coll_handler)

        self.__resetEvents()

    def acceptAll(self):
        self.acceptSelectors()

    def acceptSelectors(self):
        # mouse handlers
        self.accept('mouse1', self.__mouseSelect)
        self.accept('shift-mouse1', self.__mouseSelect, [True])
        # keyboard handlers
        self.accept('control-a', self.__selectAll)
        self.accept('control-d', self.reset)
        self.accept('control-l', self.__resetEvents, [True])

    def __resetEvents(self, wantAllEvents=False):
        self.ignoreAll()

        if config.GetBool('events-locked', True):
            wantAllEvents = bool(self.getAllAccepting()) or wantAllEvents

        if wantAllEvents:
            self.acceptAll()
        else:
            self.acceptSelectors()

    def getNetTag(self):
        return self.__tag

    def getSelection(self):
        return self.__selected

    def getSelectedKeys(self):
        return self.getSelection().getKeys()

    def isSelected(self, np):
        if np:
            return np.getKey() in self.getSelectedKeys()
        else:
            return False

    def select(self, np):
        return self.__selected.attach(np)

    def deselect(self, np):
        return np.detachNode()

    def reset(self):
        self.__resetEvents()
        for np in self.getSelection():
            flag, np = nodes.AngularNode.isAngular(np)
            self.deselect(np)

    def __getNodeAtMouse(self):
        if not base.mouseWatcherNode.hasMouse():
            return None

        mpos = base.mouseWatcherNode.getMouse()
        self.__selector_ray.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.__coll_trav.traverse(render)

        if self.__coll_handler.getNumEntries() > 0:
            self.__coll_handler.sortEntries()
            np = self.__coll_handler.getEntry(0).getIntoNodePath()
            np = np.findNetTag(self.getNetTag())
            flag, np = nodes.AngularNode.isAngular(np)
        else:
            np = None

        return np

    def __mouseSelect(self, cont=False):
        np = self.__getNodeAtMouse()
        if not np:
            if config.GetBool('empty-click-reset', True):
                self.reset()
            return

        if cont and self.isSelected(np):
            self.deselect(np)
        elif self.isSelected(np):
            pass
        else:
            self.select(np)

    def __selectAll(self):
        self.reset()
        for np in render.findAllMatches('**/=' + self.getNetTag()):
            self.select(np)
