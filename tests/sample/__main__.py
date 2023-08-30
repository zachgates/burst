import burst
import random
import sys

import panda3d.core as p3d

from direct.showbase.ShowBase import ShowBase

from PyQt5 import QtCore, QtGui, QtWidgets

from burst.character import Sprite
from burst.distributed import ClientRepository

from .gui import PandaWidget


class BurstApp(QtWidgets.QApplication):

    def exec_(self):
        base = ShowBase(windowType = 'none')
        # base.disableMouse()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout := QtWidgets.QHBoxLayout())
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.addWidget(PandaWidget(), 200)
        layout.addWidget(QtWidgets.QWidget(), 50)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._window = QtWidgets.QMainWindow()
        self._window.setWindowTitle('Burst')
        self._window.setCentralWidget(widget)
        self._window.resize(900, 600)
        self._window.show()
        self._window.raise_()

        center = self.desktop().availableGeometry().center()
        self._window.move(
            int(center.x() - self._window.width() * 0.5),
            int(center.y() - self._window.height() * 0.5),
            )

        base.cr = ClientRepository([
            'burst/dclass/direct.dc',
            'burst/dclass/burst.dc',
            'tests/sample/dclass/sample.dc',
            ])
        base.cr.accept('scene-manager-ready', self.setup)

        base.run()

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample2.burst2d', self.setup_scene)

    def setup_scene(self):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)

        background = scene.add_layer('background')
        scene.make_tile_card(row = 1, column = 1).reparent_to(background)
        base.accept('p', scene._root.ls)

        scene.add_layer('prop')
        base.accept('b', self.build_spring)

        scene.add_layer('char')
        base.accept('g', self.spawn)
        base.accept('r', self.respawn)

        base.cTrav = p3d.CollisionTraverser('traverser')
        base.cTrav.traverse(scene.get_layer('char'))
        base.cEvent = p3d.CollisionHandlerEvent()
        base.cEvent.addInPattern('%fn-into-%in')
        base.accept('DistributedNode-into-DistributedNode', self.do_spring)

        def view_colliders():
            nonlocal scene
            base.disableMouse()
            base.camera.set_pos(0, -4, 0)
            scene._root.hide()

        base._collisions = base.render.attach_new_node('collisions')
        base.accept('c', view_colliders)

        self.chars = []
        self.spawn()

    def spawn(self):
        self.chars.append(char := base.cr.createDistributedObject(
            className = 'SampleCharacter',
            zoneId = base.cr.scene_manager.get_zone(),
            ))
        char.set_bin('char', 1)
        char.b_set_tracks([
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
                name = 'Move',
                cells = [(10, 19), (10, 20), (10, 21), (10, 22), (10, 22), (10, 21), (10, 20), (10, 19)],
                frame_rate = 24,
                ),
            Sprite.Track(
                name = 'Dead',
                cells = [(10, 24)],
                frame_rate = 1,
                ),
        ])
        char.b_set_blend((60, 45, 71, 255))
        char.set_speed_factor(0.05 + random.randint(0, 100) * 0.001)
        char.startPosHprBroadcast(period = (1 / char.scene.get_frame_rate()))
        # base.accept_once('d', lambda: base.cr.sendDeleteMsg(self.char.doId))

    def respawn(self):
        for char in self.chars:
            char.b_set_action('Dead')
        self.spawn()

    def build_spring(self):
        spring = base.cr.createDistributedObject(
            className = 'Prop',
            zoneId = base.cr.scene_manager.get_zone(),
            )
        spring.set_bin('prop', 1)
        spring.b_set_tracks([
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
            ])
        spring.b_set_blend((60, 45, 71, 255))
        spring.b_set_pos(
            random.choice([-1, 1]) * min(0.8, random.random()),
            0,
            -min(0.8, max(0.1, random.random())),
            )
        spring.pose('Off')

    def do_spring(self, entry):
        char = entry.get_from_node_path().get_python_tag('realnode')
        prop = entry.get_into_node_path().get_python_tag('realnode')

        def spring_task(start, multiplier, task):
            if task.time > 1:
                return task.done

            v = (pow(task.time - 0.5, 2)
                 * ((1 / 9)
                    + ((1 / 27) * multiplier)
                 ))

            nonlocal char
            if task.time < 0.5:
                char.set_z(char.get_z() + v)
            elif task.time > 0.5:
                char.set_z(max(start.get_z(), char.get_z() - v))
            return task.cont

        prop.play('Bounce')
        base.task_mgr.add(
            spring_task,
            extraArgs = [char.get_pos(), random.randint(0, 9)],
            appendTask = True,
            )


if __name__ == '__main__':
    app = BurstApp(sys.argv)
    app.exec_()
