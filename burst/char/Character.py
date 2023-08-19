__all__ = [
    'Character',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedObject import DistributedObject

from burst.char import Mover, Responder, Sprite


class Character(DistributedObject, p3d.NodePath):

    def __init__(self, cr, sprite: Sprite):
        DistributedObject.__init__(self, cr)
        self.doId = id(self) # TODO

        p3d.NodePath.__init__(self, sprite)
        self._sprite = sprite

        self.accept(event := self.uniqueName('char_move'), self.set_moving)
        self._mover = Mover(self, event)
        self._mover.start(sprite.scene.get_frame_rate())
        self.__did_move = False

        self.accept(event := self.uniqueName('char_action'), self.set_action)
        self._responder = Responder(event)
        self._responder.register('escape', 'Dead')
        self._responder.register('space', 'Jump')
        self._responder.start(sprite.scene.get_frame_rate())
        self.__is_acting = False

        # self.accept_once('escape', self.set_action, ['Dead'])
        # self.accept('space', self.set_action, ['Jump'])
        # self.accept('space-repeat', self.set_action, ['Jump'])

    ###

    def set_bounds(self, min_: p3d.Vec3, max_: p3d.Vec3):
        self._mover.set_bounds(min_, max_)

    def get_bounds(self) -> tuple[p3d.Vec3, p3d.Vec3]:
        return self._mover.get_bounds()

    bounds = property(get_bounds, set_bounds)

    def get_speed_factor(self):
        return self._mover.get_speed_factor()

    def set_speed_factor(self, speed_factor: typing.Union[int, float]):
        self._mover.set_speed_factor(speed_factor)

    speed_factor = property(get_speed_factor, set_speed_factor)

    ###

    def set_moving(self, moving: bool):
        if self.__is_acting:
            if not self._sprite.is_playing():
                self.__is_acting = False
            return

        if moving:
            if ((self._sprite.is_playing() and not self.__did_move)
                or not self._sprite.is_playing()
                ):
                self._sprite.play('Move')
        else:
            if not self._sprite.is_playing():
                self._sprite.play('Idle')

        self.__did_move = moving

    def set_action(self, action: str):
        if action == 'Dead':
            self._mover.stop()
            self._responder.stop()
            self._sprite.pose('Dead')
            return

        if self.__is_acting:
            return

        if action == 'Jump':
            self._sprite.play('Jump')
            self.__is_acting = True
