__all__ = [
    'Character',
]


from burst.character import Character


class SampleCharacter(Character):

    def __init__(self, cr):
        super().__init__(cr)

        self._watch_button('escape', 'Dead')
        self._watch_button('space', 'Jump')

        self._action = ''
        self.__task = None
        self.__is_moving = False
        self.__is_acting = False

    def generate(self):
        super().generate()
        if self.cr.isLocalId(self.doId):
            self.__task = base.task_mgr.do_method_later(
                (1 / self.scene.get_frame_rate()),
                self._watch,
                name = f'{self._watch!r}',
                extraArgs = [], # hack to trigger appendTask=False
                )

    def set_moving(self, is_moving: bool):
        if is_moving:
            self.b_set_action('Move')
        else:
            self.b_set_action('Idle')

    def get_action(self) -> str:
        return self._action

    def set_action(self, action: str):
        if action not in self._tracks:
            print(f'unknown action: {action}')
            return

        # interrupt both acting and moving
        if action == 'Dead':
            if self.__task is not None:
                base.task_mgr.remove(self.__task)
            self.pose('Dead')
            self._action = 'Dead'
            return

        if self.__is_acting:
            if self.is_playing():
                return # we are still acting
            else: # we were acting; done now
                self.__is_acting = False

        if action == 'Jump':
            if ((self.is_playing() and not self.__is_acting)
                or not self.is_playing()
                ):
                self.play('Jump')
                self.__is_acting = True # we are now acting
        elif action == 'Move':
            if ((self.is_playing() and not self.__is_moving)
                or not self.is_playing()
                ):
                self.play('Move')
                self.__is_acting = False # we interrupted acting
                self.__is_moving = True # we are now moving
        elif action == 'Idle':
            if not self.is_playing(): # are we busy ?
                self.play('Idle') # no, and
                self.__is_moving = False # we are not moving
        else:
            raise ValueError(f'unknown action: {action!r}')

        self._action = action
