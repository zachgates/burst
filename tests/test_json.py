import burst

from pprint import pprint

from direct.directbase.DirectStart import base


scene = burst.store.load_file('data/scenes/sample.burst3d')
pprint(scene.read())
base.run()
