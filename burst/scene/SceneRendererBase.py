__all__ = ['SceneRendererBase']


from typing import Tuple

import panda3d.core as p3d

from direct.showbase.DirectObject import DirectObject


class SceneRendererBase(DirectObject):

    def __init__(self, title: str, resolution: Tuple[int, int]):
        super().__init__()
        self.adjust_window(title, resolution)

    def adjust_window(self, title: str, resolution: Tuple[int, int]):
        prop = p3d.WindowProperties()
        prop.set_title(title)
        prop.set_size(resolution)
        base.win.request_properties(prop)
