__all__ = [
    'Responder',
]


from panda3d import core as p3d

from direct.showbase.DirectObject import DirectObject


class Responder(object):

    def __init__(self, action_event: str, done_event: str):
        super().__init__()
        self._task = None
        self.__actions = dict()
        self.__action_event = action_event

    ###

    def start(self, frame_rate: int):
        self._task = base.task_mgr.do_method_later(
            (1 / frame_rate),
            self._respond, f'{self._respond!r}',
            appendTask = True,
            )

    def stop(self):
        base.task_mgr.remove(self._task)

    ###

    def register(self, button: str, action: str):
        if action in self.__actions:
            raise Exception('action already bound')
        else:
            self.__actions[action] = button

    def _respond(self, task):
        for action, button in self.__actions.items():
            if base.mouseWatcherNode.is_button_down(button):
                base.messenger.send(self.__action_event, [action])
                break

        return task.again
