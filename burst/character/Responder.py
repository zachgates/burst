__all__ = [
    'Responder',
]


from direct.distributed.DistributedObject import DistributedObject
from direct.task import Task


class Responder(DistributedObject):

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self._button_map = dict()

    def _watch_button(self, button: str, action: str):
        if button in self._button_map:
            raise ValueError(f'already registered: {button!r}')
        else:
            self._button_map[button] = action

    def _watch(self, hook = (lambda *a, **kw: None)):
        for button, action in self._button_map.items():
            if base.mouseWatcherNode.is_button_down(button):
                hook(action)
                break

        return Task.again
