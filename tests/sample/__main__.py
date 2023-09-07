import builtins
import burst
import random
import sys

import panda3d.core as p3d

from PyQt5 import QtCore, QtGui, QtWidgets

from burst.character import Sprite
from burst.distributed import ClientRepository
from burst.gui import PandaApp, PandaWidget


class BurstApp(PandaApp):

    TC_DOID = 0
    TC_ACTION = 1

    def test(self):
        print(
            f'{self.window = }',
            f'{self.window.metaObject().className() = }',
            f'{self.window.objectName() = }',
            f'{self.window.windowHandle() = }',
            ('{self.window.windowHandle().objectName() = }'
             if self.window.windowHandle() is None else
             f'{self.window.windowHandle().objectName() = }'
             ),
            '',
            f'{self.window.window() = }',
            f'{self.window.window().metaObject().className() = }',
            f'{self.window.window().objectName() = }',
            f'{self.window.window().windowHandle() = }',
            ('{self.window.window().windowHandle().objectName() = }'
             if self.window.window().windowHandle() is None else
             f'{self.window.window().windowHandle().objectName() = }'
             ),
            '',
            *((f'{self.window.parent() = }',)
              if self.window.parent() is None else
              (f'{self.window.parent() = }',
               f'{self.window.parent().metaObject().className() = }',
               f'{self.window.parent().objectName() = }',
               f'{self.window.parent().windowHandle() = }',
               f'{self.window.parent().windowHandle().objectName() = }',
               )),
            '',
            f'{self.widget = }',
            f'{self.widget.metaObject().className() = }',
            f'{self.widget.objectName() = }',
            f'{self.widget.windowHandle() = }',
            f'{self.widget.windowHandle().objectName() = }',
            '',
            f'{self.widget.window() = }',
            f'{self.widget.window().metaObject().className() = }',
            f'{self.widget.window().objectName() = }',
            f'{self.widget.window().windowHandle() = }',
            f'{self.widget.window().windowHandle().objectName() = }',
            '',
            f'{self.widget.parent() = }',
            f'{self.widget.parent().metaObject().className() = }',
            f'{self.widget.parent().objectName() = }',
            f'{self.widget.parent().windowHandle() = }',
            f'{self.widget.parent().windowHandle().objectName() = }',
            '',
            sep = '\n',
            )
        self.pw.test()

    def resize_it(self, pw):
        # scene = base.cr.scene_manager.get_scene()
        # props = p3d.WindowProperties()
        # scene.set_resolution((256, 256))
        # print(pw.size())
        print(pw.subwindow.parent())
        print(self.window.windowHandle())
        print(self.focusWindow())
        print(pw.subwindow.parent() == pw.container)
        print(pw.subwindow.parent().parent().parent().parent())
        # exit()
        # pw.subwindow.resize(pw.container.size().width() // 2, pw.container.size().height() // 2)
        # pw.container.updateGeometry()
        # pw.container.resize(pw.size().width(), pw.size().height())
        # print(pw.size())
        # base.win.requestProperties(props)

    def do_window_event(self, window):
        # print(dir(window.get_gsg()))
        print('window-event')
        print(burst.window.size())
        print(self.widget.size())
        print(self.pw.size())
        print(self.pw.container.size())
        print(self.pw.subwindow.size())
        print(self.pw.subwindow.parent().size())
        print(base.win.get_x_size(), base.win.get_y_size())
        print()
        # self.pw.container.resize(80, 80)
        # self.pw.subwindow.resize(64, 64)
        # props = p3d.WindowProperties()
        # props.setSize(self.pw.subwindow.size().width(), self.pw.subwindow.size().height())
        # base.win.requestProperties(props)

    def exec_(self):
        self.window = burst.window = QtWidgets.QMainWindow()
        widget = self.widget = QtWidgets.QWidget(self.window)

        # if base.win is None:
        #     props = p3d.WindowProperties.getConfigProperties()
        # #     # print(self.size().width(), self.size().height())
        # #     # props.setSize(self.size().width(), self.size().height())
        # #     # props.setSize(600, 600)
        # #     # props.setUndecorated(True)
        #     # props.setParentWindow(int(self.widget.winId()))
        # #     # props.setForeground(True)
        #     base.openDefaultWindow(props = props)

        # handle = base.win.getWindowHandle().getIntHandle()
        # self.subwindow = QtGui.QWindow.fromWinId(handle)
        # self.container = QtWidgets.QWidget.createWindowContainer(
        #     self.subwindow,
        #     parent = self.widget,
        #     flags = QtCore.Qt.SubWindow,
        #     )

        # props = p3d.WindowProperties.getConfigProperties()
        # props.setParentWindow(int(self.container.winId()))
        # base.win.requestProperties(props)

        layout = QtWidgets.QGridLayout(widget)
        layout.addWidget(pw := PandaWidget(widget), 0, 0, 2, 1)
        layout.addWidget(tree := QtWidgets.QTreeWidget(), 0, 1, 1, 1)
        layout.addWidget(QtWidgets.QTreeWidget(), 1, 1, 1, 1)
        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(10)
        layout.setColumnStretch(0, 1)
        # layout.setRowStretch(0, 1)
        # layout.setRowStretch(1, 1)

        self.accept('o', self.resize_it, [pw])
        # self.accept('aspectRatioChanged', lambda: print('aspectRatioChanged'))
        self.accept('window-event', self.do_window_event)
        self.accept('w', self.do_window_event, [None])
        self.accept('i', self.test)

        self.pw = pw
        pw.setAutoFillBackground(True)
        p = pw.palette()
        p.setColor(pw.backgroundRole(), QtCore.Qt.red)
        pw.setPalette(p)

        self.pw.container.setAutoFillBackground(True)
        p = self.pw.container.palette()
        p.setColor(self.pw.container.backgroundRole(), QtCore.Qt.blue)
        self.pw.container.setPalette(p)

        props = base.win.getRequestedProperties()
        print('!', props.get_x_size(), props.get_y_size())
        burst.window.setCentralWidget(widget)
        burst.window.setWindowTitle(props.get_title())
        self.test()
        burst.window.show()
        # burst.window.resize(props.get_x_size(), props.get_y_size())
        print('!')
        burst.window.raise_()
        self.do_window_event(None)
        self.test()

        # props = p3d.WindowProperties()
        # # print(self.size().width(), self.size().height())
        # props.setSize(self.pw.container.size().width(), self.pw.container.size().height())
        # # props.setUndecorated(True)
        # props.setParentWindow(int(pw.winId()))
        # props.setForeground(True)
        # base.win.requestProperties(props)

        burst.window.tree = tree
        burst.window.tree.setColumnCount(2)

        header = burst.window.tree.headerItem()
        header.setText(self.TC_DOID, 'Characters')
        header.setText(self.TC_ACTION, 'Action')

        center = self.desktop().availableGeometry().center()
        burst.window.move(
            int(center.x() - (burst.window.width() * 0.5)),
            int(center.y() - (burst.window.height() * 0.5)),
            )

        base.disableMouse()
        print(dir(base.taskMgr))
        print(base.taskMgr.getAllTasks())
        base.run()

    def load(self):
        print('open_main_window')
        base.cr = ClientRepository([
            'burst/dclass/direct.dc',
            'burst/dclass/burst.dc',
            'tests/sample/dclass/sample.dc',
            ])
        base.cr.accept('scene-manager-ready', self.setup)

    def setup(self):
        base.cr.scene_manager.request('data/scenes/sample4.burst2d', self.setup_scene)

    def setup_scene(self):
        scene = base.cr.scene_manager.get_scene()
        scene.set_frame_rate(60)
        # scene.set_resolution((640, 512))

        background = scene.add_layer('background')
        bg = scene.tiles(0).make_tile_card(row = 1, column = 1)
        bg.reparent_to(background)
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
        char.b_set_tilesheet(0)
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

        scene = base.cr.scene_manager.get_scene()
        char.startPosHprBroadcast(period = (1 / scene.get_frame_rate()))
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
        spring.b_set_tilesheet(0)
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
    builtins.app = BurstApp(sys.argv)
    builtins.app.exec_()
