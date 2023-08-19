__all__ = [
    'AIRepository',
]


import typing

from panda3d import core as p3d

from direct.distributed.ClientRepository import ClientRepository


class AIRepository(ClientRepository):

    def __init__(self, dcFileNames: typing.Iterable[str] = []):
        """ The AI Repository usually lives on a server and is responsible for
        server side logic that will handle game objects """

        super().__init__(
            dcFileNames = dcFileNames,
            dcSuffix = 'AI',
            threadedNet = True,
            )

        tcpPort = p3d.ConfigVariableInt('server-port', 4400).get_value()
        hostname = p3d.ConfigVariableString('server-host', '127.0.0.1').get_value()

        # Attempt a connection to the server
        self.connect(
            [p3d.URLSpec('http://{}:{}'.format(hostname, tcpPort))],
            successCallback = self.connectSuccess,
            failureCallback = self.connectFailure,
            )

    def connectFailure(self, statusCode, statusString):
        """ something went wrong """
        print("Couldn't connect. Make sure to run server.py first!")
        raise Exception(statusString)

    def connectSuccess(self):
        """ Successfully connected.  But we still can't really do
        anything until we've got the doID range. """
        # The Client Repository will throw this event as soon as it has a doID
        # range and would be able to create distributed objects
        self.accept('createReady', self.gotCreateReady)

    def lostConnection(self):
        """ This should be overridden by a derived class to handle an
         unexpectedly lost connection to the gameserver. """
        exit()

    def gotCreateReady(self):
        """ Now we're ready to go! """

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet
        if not self.haveCreateAuthority():
            # Not ready yet.
            return

        # we are ready now, so ignore further createReady events
        self.ignore('createReady')

        # Create a Distributed Object by name.  This will look up the object in
        # the dc files passed to the repository earlier
        self.timeManager = self.createDistributedObject(
            className = 'TimeManagerAI', # The Name of the Class we want to initialize
            zoneId = 1, # The Zone this Object will live in
            )

        # self.gameDistObject = self.createDistributedObject(
        #     className = 'CharacterAI',
        #     zoneId = 2,
        #     )

        print("AI Repository Ready")

    def deallocateChannel(self, doID):
        """ This method will be called whenever a client disconnects from the
        server.  The given doID is the ID of the client who left us. """
        print("Client left us: ", doID)
