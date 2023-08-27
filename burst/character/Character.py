__all__ = [
    'Character',
]


import typing

from panda3d import core as p3d

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

from burst.character import Collider, Mover, Responder, Sprite, SpriteData


class Character(Collider, DistributedSmoothNode):

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        self.set_transparency(p3d.TransparencyAttrib.MAlpha)

        scene = base.cr.scene_manager.get_scene()
        self.reparent_to(scene.get_layer('char'))

        factor = 4
        self.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        Collider.__init__(self, cr, (self.get_sx() * 0.5), 'char', 'prop')

        self._sprite_data = SpriteData('sprite', [], p3d.LColor())
        self._sprite = None

        self._mover = None
        self.__did_move = False

        self._responder = None
        self.__is_acting = False

        self._is_active = False

    def generate(self):
        print(f'Character.generate {self.doId}')
        DistributedSmoothNode.generate(self)

        self.accept(event := self.uniqueName('char_move'), self.b_set_moving)
        self._mover = Mover(self, event)
        self._mover.set_bounds(
            p3d.Vec3((self.get_sx() - 1), 0, (self.get_sz() - 1)),
            p3d.Vec3(abs(self.get_sx() - 1), 0, abs(self.get_sz() - 1)),
            )

        self.accept(event := self.uniqueName('char_action'), self.b_set_action)
        self._responder = Responder(event)
        self._responder.register('escape', 'Dead')
        self._responder.register('space', 'Jump')

        if self.cr.isLocalId(self.doId):
            base.cTrav.add_collider(self._collider, base.cEvent)

    def disable(self):
        print(f'Character.disable {self.doId}')
        DistributedSmoothNode.disable(self)

    def delete(self):
        Collider.delete(self)
        DistributedSmoothNode.delete(self)
        print(f'Character.delete {self.doId}')

    ###

    def get_sprite(self) -> SpriteData:
        return self._sprite_data

    def set_sprite(self, data):
        print(f'Character({self.doId}).set_sprite')
        print(data)

        if self._sprite:
            print('remove_child')
            self.node().remove_child(self._sprite)

        self._sprite_data = SpriteData(*data)
        scene = base.cr.scene_manager.get_scene()
        self._sprite = scene.make_sprite(self._sprite_data)
        self.node().add_child(self._sprite)
        print('add_child')

    def d_set_sprite(self, data):
        self.sendUpdate('set_sprite', [data])

    def b_set_sprite(self, data):
        self.set_sprite(data)
        self.d_set_sprite(data)

    ###

    def get_active(self):
        return self._is_active

    def set_active(self, is_active: bool):
        print(f'Character({self.doId}).set_active({is_active})')

        if not is_active:
            if self._is_active:
                print(f'stop activity {self.doId}')
                self._mover.stop()
                self._responder.stop()
        else:
            if not self._is_active:
                if not base.cr.isLocalId(self.doId):
                    return

                scene = base.cr.scene_manager.get_scene()
                self._mover.start(scene.get_frame_rate())
                self._responder.start(scene.get_frame_rate())

        self._is_active = is_active

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
            print(f'Dead {self.doId}')
            self.set_active(False)
            self._sprite.pose('Dead')
            self.__is_acting = True
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
