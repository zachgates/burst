import argparse

from direct.showbase.ShowBase import ShowBase

from . import AIRepository, ServerRepository


parser = argparse.ArgumentParser(
    prog = 'burst.ai',
    description = 'Burst Server Module',
    )

parser.add_argument(
    '--dclass',
    type = str,
    action = 'append',
    default = [
        'data/dclass/direct.dc',
        'data/dclass/burst.dc',
    ])


args = parser.parse_args()
base = ShowBase(windowType = 'none')
server = ServerRepository(args.dclass)
base.air = AIRepository(args.dclass)
base.run()
