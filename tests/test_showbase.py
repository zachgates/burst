import burst
import random

import panda3d.core as p3d

from direct.interval.IntervalGlobal import Func, Parallel, Sequence
from direct.showbase.ShowBase import ShowBase

from burst.character import Character, Collider, Sprite, SpriteData
from burst.distributed import ClientRepository


CHAR_MASK = p3d.BitMask32(0x0F)
PROP_MASK = p3d.BitMask32(0xF0)


class BurstApp(ShowBase):

    def do_spring(self, entry):
        char = entry.get_from_node_path().get_python_tag('realnode')
        # char.set_active(False)

        prop = entry.get_into_node_path().get_python_tag('realnode')
        spring = prop.get_python_tag('sprite')

        def spring_task(start, task):
            nonlocal char
            if task.time > 1:
                return task.done
            v = pow(task.time - 0.5, 2) * (2 / 9)
            if task.time < 0.5:
                char.set_pos(p3d.Vec3(char.get_x(), 0, char.get_z() + v))
            elif task.time > 0.5:
                char.set_pos(p3d.Vec3(char.get_x(), 0, max(start.get_z(), char.get_z() - v)))
            return task.cont

        spring.play('Bounce')
        base.task_mgr.add(
            spring_task,
            extraArgs = [char.get_pos()],
            appendTask = True,
            )

    def build_spring(self):
        scene = base.cr.scene_manager.get_scene()
        spring = scene.make_sprite(SpriteData(
            name = 'spring',
            tracks = [
                Sprite.Track(
                    name = 'Off',
                    cells = [(6, 22)],
                    frame_rate = 1,
                    ),
                Sprite.Track(
                    name = 'Bounce',
                    cells = [(6, 22), (6, 23), (6, 24), (6, 23), (6, 22)],
                    frame_rate = 30,
                    ),
                ],
            blend = p3d.LColor(60, 45, 71, 255),
            ))

        springNP = scene.get_layer('prop').attach_new_node(spring)
        springNP.set_python_tag('sprite', spring)
        springNP.set_bin('prop', 1)
        springNP.set_transparency(p3d.TransparencyAttrib.MAlpha)
        springNP.set_pos(random.choice([-1, 1]) * min(0.8, random.random()), 0, -min(0.8, max(0.1, random.random())))

        factor = 4
        springNP.set_scale(p3d.Vec3(
            (scene.tiles.rules.tile_size.x / scene.resolution.x) * factor,
            1,
            (scene.tiles.rules.tile_size.y / scene.resolution.y) * factor,
            ))

        spring.pose('Off')

        collider = Collider(springNP, springNP.get_sx() * 0.5, 'none', 'char')
        collider.reparent_to(self._collisions)
        collider.set_pos(springNP.get_x(), 0, springNP.get_z())

    def respawn(self):
        for char in self.chars:
            char.set_action('Dead')
        self.spawn()

    def spawn(self):
        scene = base.cr.scene_manager.get_scene()
        self.chars.append(char := base.cr.createDistributedObject(
            className = 'Character',
            zoneId = base.cr.scene_manager.get_zone(),
            ))
        char.set_bin('char', 1)
        char.b_set_sprite(SpriteData(
            name = 'sprite',
            tracks = [
                Sprite.Track(
                    name = 'Idle',
                    cells = [(10, 19), (10, 23), (10, 23), (10, 19)],
                    frame_rate = 4,
                    ),
                Sprite.Track(
                    name = 'Jump',
                    cells = [(10, 19), (10, 23), (10, 22), (10, 21), (10, 19)],
                    frame_rate = 10,
                    ),
                Sprite.Track(
                    'Move',
                    cells = [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)],
                    frame_rate = 24,
                    ),
                Sprite.Track(
                    name = 'Dead',
                    cells = [(10, 24)],
                    frame_rate = 1,
                    ),
            ],
            blend = p3d.LColor(60, 45, 71, 255),
            ))
        char.set_active(True)
        char.set_speed_factor(0.05 + random.randint(0, 100) * 0.001)
        char.startPosHprBroadcast(period = (1 / scene.get_frame_rate()))
        # self.accept_once('d', lambda: base.cr.sendDeleteMsg(self.char.doId))

    def setup_scene(self, zone):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)

        background = scene.add_layer('background')
        scene.make_tile_card(row = 1, column = 1).reparent_to(background)
        self.accept('p', scene._root.ls)

        scene.add_layer('prop')
        self.accept('b', self.build_spring)

        scene.add_layer('char')
        self.accept('g', self.spawn)
        self.accept('r', self.respawn)

        base.cTrav = p3d.CollisionTraverser('traverser')
        base.cTrav.traverse(scene.get_layer('char'))
        base.cEvent = p3d.CollisionHandlerEvent()
        base.cEvent.addInPattern('%fn-into-%in')
        self.accept('DistributedNode-into-spring', self.do_spring)

        def view_colliders():
            nonlocal scene
            base.disableMouse()
            base.camera.set_pos(0, -4, 0)
            scene._root.hide()

        self._collisions = base.render.attach_new_node('collisions')
        self.accept('c', view_colliders)

        self.chars = []
        self.spawn()

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample2.burst2d', self.setup_scene)

    def run(self):
        self.cr = ClientRepository(['data/dclass/direct.dc', 'data/dclass/burst.dc'])
        self.cr.accept('scene-manager-ready', self.setup)
        super().run()


if __name__ == '__main__':
    base = BurstApp()
    base.run()
