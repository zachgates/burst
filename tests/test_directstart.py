import burst
import typing

import panda3d.core as p3d

from direct.directbase.DirectStart import base


def StaticFrame(scene, cell: tuple[int, int]) -> p3d.PandaNode:
    """Simple factory for static frames."""
    return scene.make_tile(cell).node()


def SpriteFrame(scene,
                name: str,
                cells: typing.Iterable[tuple[int, int]] = [],
                ) -> p3d.SequenceNode:
    """Simple factory for animated frames."""
    node = p3d.SequenceNode(name)
    for cell in cells:
        node.add_child(StaticFrame(scene, cell))
    return node


if __name__ == '__main__':
    scene = burst.store.load_file('tests/data/scenes/sample.burst2d').read()
    aspect2d.attach_new_node(sprite := SpriteFrame(scene, 'sprite', [
        (9, 19),
        (9, 23),
        (9, 21),
        (9, 22),
        ]))
    sprite.set_frame_rate(12)
    sprite.pingpong(True)
    base.run()
