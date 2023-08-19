from direct.showbase.ShowBase import ShowBase

from . import AIRepository, ServerRepository


dcFileNames =[
    'data/dclass/direct.dc',
    'data/dclass/burst.dc',
]


base = ShowBase(windowType = 'none')
server = ServerRepository(dcFileNames)
base.air = AIRepository(dcFileNames)
base.run()
