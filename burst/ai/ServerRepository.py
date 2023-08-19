__all__ = [
    'ServerRepository',
]


import typing

from panda3d import core as p3d

from direct.distributed.ServerRepository import ServerRepository


class ServerRepository(ServerRepository):

    def __init__(self, dcFileNames: typing.Iterable[str] = []):
        tcpPort = p3d.ConfigVariableInt('server-port', 4400).get_value()
        super().__init__(
            tcpPort,
            dcFileNames = dcFileNames,
            threadedNet = True,
            )
