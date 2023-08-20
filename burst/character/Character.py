__all__ = [
    'Character',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

from burst.character import Mover, Responder, Sprite, SpriteData


class Character(DistributedSmoothNode):

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)

        self._sprite = None

        self._mover = None
        self.__did_move = False

        self._responder = None
        self.__is_acting = False

    def generate(self):
        print(f'new Character {self.doId}')
        DistributedSmoothNode.generate(self)

        self.accept(event := self.uniqueName('char_move'), self.b_set_moving)
        self._mover = Mover(self, event)
        self._mover.start(60)#self._sprite.scene.get_frame_rate())

        self.accept(event := self.uniqueName('char_action'), self.b_set_action)
        self._responder = Responder(event)
        self._responder.register('escape', 'Dead')
        self._responder.register('space', 'Jump')
        self._responder.start(60)#self._sprite.scene.get_frame_rate())

        # self.accept_once('escape', self.set_action, ['Dead'])
        # self.accept('space', self.set_action, ['Jump'])
        # self.accept('space-repeat', self.set_action, ['Jump'])

        messenger.send('character-ready', [self])

    def set_sprite(self, data):
        name, tracks, blend = data

        if self._sprite:
            self.node().remove_child(self._sprite)

        scene = base.scene_manager.get_scene()
        self._sprite = scene.make_sprite(name)
        self.node().add_child(self._sprite)

        for track in tracks:
            self._sprite.add_track(Sprite.Track(*track))
        self._sprite.set_blend(p3d.LColor(*blend))

    ### Mover

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

    def set_moving(self, is_moving: bool):
        if self.__is_acting:
            if not self._sprite.is_playing():
                self.__is_acting = False
            return

        if is_moving:
            if ((self._sprite.is_playing() and not self.__did_move)
                or not self._sprite.is_playing()
                ):
                self.b_set_action('Move')
                self.__did_move = True
        else:
            if not self._sprite.is_playing():
                self._sprite.play('Idle')
                self.__did_move = False

    def d_set_moving(self, is_moving: bool):
        self.sendUpdate('set_moving', [is_moving])

    def b_set_moving(self, is_moving: bool):
        self.set_moving(is_moving)
        self.d_set_moving(is_moving)

    ###

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
        elif action == 'Move':
            self._sprite.play('Move')
            self.__is_acting = False

    def d_set_action(self, action: str):
        self.sendUpdate('set_action', [action])

    def b_set_action(self, action: str):
        self.set_action(action)
        self.d_set_action(action)
