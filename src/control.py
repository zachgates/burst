import functools
import uuid

from panda3d.core import *

from direct.showbase.DirectObject import DirectObject

from .base import File, FileError


class FileManager(DirectObject):

    _fext = None

    def load(self, fpath, silent=False, recursive=False):
        fobj = vfs.getFile(fpath)
        try:
            if fobj and fobj.isRegularFile():
                return self.loadFile(fobj, silent)
            elif fobj and fobj.isDirectory():
                return self.loadDirectory(fobj, silent, recursive)
            else:
                return None
        except AttributeError as e:
            if not silent:
                raise e
            else:
                return None

    def loadFile(self, fobj, silent=False):
        try:
            ftype = File.find_class_by_fext(self._fext)
            return ftype(fobj.getFilename())
        except FileError as e:
            if not silent:
                raise e
            else:
                return None

    def loadDirectory(self, fobj, silent=False, recursive=False):
        for virtualFile in vfs.scanDirectory(fobj.getFilename()):
            if virtualFile.isDirectory() and not recursive:
                continue
            elif virtualFile.isDirectory():
                for file_ in self.loadDirectory(fobj, silent, recursive):
                    yield file_
            elif virtualFile.isRegularFile():
                yield self.loadFile(virtualFile, silent)
            else:
                yield None


class SelectionManager(DirectObject):

    def __init__(self, tag=None):
        DirectObject.__init__(self)
        self.__tag = str(tag) or uuid.uuid4().hex

        self.__coll_trav = CollisionTraverser('trav-%s' % self.getNetTag())
        self.__coll_handler = CollisionHandlerQueue()

        self.__selected = NodePathCollection()
        self.__selector_ray = CollisionRay()
        self.__selector_node = CollisionNode('mouse-%s' % self.getNetTag())
        self.__selector_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.__selector_node.addSolid(self.__selector_ray)

        np = camera.attachNewNode(self.__selector_node)
        self.__coll_trav.addCollider(np, self.__coll_handler)

        self.accept('mouse1', self.__mouseSelect)
        self.accept('shift-mouse1', self.__mouseSelect, [True])

    def getNetTag(self):
        return self.__tag

    def getSelection(self):
        sel = NodePathCollection()
        sel.extend(self.__selected)
        return sel

    def getSelectedPaths(self):
        return self.__selected.getPaths()

    def isSelected(self, np):
        if np:
            return self.__selected.hasPath(np)
        else:
            return False

    def select(self, np):
        self.__selected.addPath(np)
        return np

    def deselect(self, np):
        self.__selected.removePath(np)
        return np

    def reset(self):
        for np in self.getSelectedPaths():
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
        else:
            np = None

        return np

    def __mouseSelect(self, cont=False):
        sl = self.getSelection()
        np = self.__getNodeAtMouse()

        if not np:
            self.reset()
            return

        if not cont:
            self.reset()

        if sl.hasPath(np):
            self.deselect(np)
        else:
            self.select(np)
