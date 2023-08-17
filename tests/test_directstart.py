import burst

from direct.directbase.DirectStart import base


if __name__ == '__main__':
    scene = burst.store.load_file('tests/data/scenes/sample.burst2d').read()
    sprite = burst.char.Sprite(scene, 'sprite')
    sprite.add_track('Idle', [(9, 19), (9, 23), (9, 22), (9, 21)])
    sprite.set_frame_rate(8)
    sprite.loop('Idle')
    spriteNP = base.aspect2d.attach_new_node(sprite)
    base.run()
