from panda3d import core as p3d

import direct.directbase.DirectStart


def StaticFrame(scene, index: int) -> p3d.NodePath:
    """Simple factory for static frames."""
    return scene.make_tile(index)


def SpriteFrame(scene, name: str, frames = []) -> p3d.NodePath:
    """Simple factory for animated frames."""
    node = p3d.SequenceNode(name)
    for index in frames:
        tile_node = StaticFrame(scene, index)
        node.add_child(tile_node.node())
    return node


if __name__ == '__main__':
    scene = burst.store.load_file('tests/data/scenes/sample.burst').read()
    sprite = SpriteFrame(scene, 'Actor-Foo', [275, 279, 277, 278])
    sprite.set_frame_rate(12)
    sprite.pingpong(True)
    aspect2d.attach_new_node(sprite)
    base.run()
