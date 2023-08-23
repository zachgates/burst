import burst
import dataclasses
import random

import panda3d.core as p3d

from direct.interval.IntervalGlobal import Func, Parallel, Sequence
from direct.showbase.ShowBase import ShowBase

from burst.character import Character, Sprite, SpriteData
from burst.distributed import ClientRepository


CHAR_MASK = p3d.BitMask32(0x0F)
PROP_MASK = p3d.BitMask32(0xF0)


class BurstApp(ShowBase):

    def do_spring(self, entry):
        char = entry.get_from_node_path().get_python_tag('realnode')
        # char.set_active(False)

        prop = entry.get_into_node_path().get_python_tag('realnode')
        spring = prop.get_python_tag('sprite')

        def spring_task(task):
            nonlocal char
            if task.time > 1:
                return task.done
            elif task.time < 0.5:
                char.set_pos(p3d.Vec3(char.get_x(), 0, char.get_z() + 0.02))
            elif task.time > 0.5:
                char.set_pos(p3d.Vec3(char.get_x(), 0, char.get_z() - 0.02))
            return task.cont

        spring.play('Bounce')
        base.task_mgr.add(spring_task, appendTask = True)

        # Parallel(
        #     Func(spring.play, 'Bounce'),
        #     char.posInterval(
        #         0.5,
        #         pos = p3d.Point3(char.get_x(), 0, char.get_z() + 0.5),
        #         startPos = char.get_pos(),
        #         blendType = 'easeInOut',
        #     )).start()

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

        springNP = scene.get_background().attach_new_node(spring)
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

        cnode = p3d.CollisionNode('prop_spring')
        cnode.set_from_collide_mask(p3d.BitMask32.allOff())
        cnode.set_into_collide_mask(CHAR_MASK)
        csphere = p3d.CollisionSphere(0, 0, 0, springNP.get_sx() * 0.5)
        csnp = scene._collisions.attach_new_node(cnode)
        csnp.set_python_tag('realnode', springNP)
        csnp.set_pos(springNP.get_x(), springNP.get_z(), 0)
        csnp.node().add_solid(csphere)
        csnp.show()

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
        char.b_set_sprite(dataclasses.astuple(SpriteData(
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
            )))
        char.set_active(True)
        char.set_speed_factor(0.05 + random.randint(0, 100) * 0.001)
        char.startPosHprBroadcast(period = (1 / scene.get_frame_rate()))

        char._cnode.set_from_collide_mask(CHAR_MASK)
        char._cnode.set_into_collide_mask(PROP_MASK)
        base.cTrav.addCollider(char._csnp, base.cEvent)

        # self.accept_once('d', lambda: base.cr.sendDeleteMsg(self.char.doId))

    def setup_scene(self, zone):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)

        base.cTrav = p3d.CollisionTraverser('traverser')
        base.cTrav.traverse(scene.get_background())

        # base.cQueue = p3d.CollisionHandlerQueue()
        #
        # def check_queue(task):
        #     base.cQueue.sort_entries()
        #     print(dir(base.cQueue.entries))
        #     for entry in base.cQueue.entries:
        #         print(entry)
        #     return task.again
        #
        # base.task_mgr.do_method_later(1, check_queue, 'cg', appendTask = True)

        self.cEvent = p3d.CollisionHandlerEvent()
        self.cEvent.addInPattern('%fn-into-%in')
        self.accept('char-into-prop_spring', self.do_spring)

        bgNP = scene.get_background()
        bgNP.set_texture(scene.get_tile(row = 1, column = 1))
        # bgNP.hide()
        self.accept('p', scene.get_background().ls)

        scene.add_layer('prop')
        self.accept('b', self.build_spring)

        scene.add_layer('char')
        self.accept('g', self.spawn)
        self.accept('r', self.respawn)

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
