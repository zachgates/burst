import burst

from direct.directbase.DirectStart import base


if __name__ == '__main__':
    scene = burst.store.load_file('data/scenes/sample3.burst2d').read()

    # hack to get around the distributed stuff
    class dummy(object): pass
    base.cr = dummy()
    setattr(base.cr, 'scene_manager', dummy())
    setattr(base.cr.scene_manager, 'get_scene', (lambda: scene))

    sprite = burst.character.Sprite(base.cr, 'sprite') # cr is None
    sprite.set_tilesheet(0)
    sprite.add_track(burst.character.Sprite.Track(
        name = 'Idle',
        cells = [(9, 19), (9, 23), (9, 22), (9, 21)],
        frame_rate = 8,
        ))
    sprite.loop('Idle')
    sprite.reparent_to(scene.add_layer('char'))
    sprite.set_scale(1) # counter scale factor in Character
    base.run()
