#!/usr/local/bin/python3.9

from pprint import pprint

from panda3d import core as p3d

from direct.directbase.DirectStart import base
from direct.interval.LerpInterval import LerpFunc

from libpandaworld.nodes import AngularNode


WHEEL = loader.load_model('wheel.bam')
# WHEEL.set_transparency(p3d.TransparencyAttrib.M_alpha)
# WHEEL.set_alpha_scale(0.25)
WHEEL.set_render_mode_wireframe()
WHEEL.set_render_mode_thickness(8)


MARKER = loader.load_model('smiley.egg').get_child(0)
MARKER.set_name('marker')
MARKER.set_scale(0.025)
MARKER.set_texture_off(True)


WHEEL = AngularNode(parent = render, node = WHEEL)
MARKERS = WHEEL.attach(p3d.NodePath('markers'))


for geom_node in WHEEL.find_all_matches('**/+GeomNode'):
    for n in range(geom_node.node().get_num_geoms()):
        geom = geom_node.node().get_geom(n)
        data = geom.get_vertex_data()

        for k in range(geom.get_num_primitives()):
            prim = geom.get_primitive(k)
            prim = prim.decompose()
            # print(prim)

        vertex = p3d.GeomVertexReader(data, 'vertex')
        points = dict()

        n = 0
        while not vertex.is_at_end():
            point = vertex.get_data3()
            points.setdefault(point, [])
            points[point].append(n)
            n += 1

        for point in points:
            marker = MARKER.copy_to(MARKERS)
            marker.set_pos(point)


WHEEL.set_axis(AngularNode.AXES.INTERNAL)
WHEEL.set_pos(-WHEEL.get_tight_center())
ival = LerpFunc(WHEEL.set_h, 5.0, 0, 360)
ival.loop()

base.camera.set_pos(0, -4, 2.3)
base.camera.set_hpr(0, -30, 0)
base.disable_mouse()
base.run()
