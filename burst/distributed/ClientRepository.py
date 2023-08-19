__all__ = [
    'ClientRepository',
]


import typing

from panda3d import core as p3d

from direct.distributed.ClientRepository import ClientRepository


class ClientRepository(ClientRepository):

    def __init__(self, dcFileNames: typing.Iterable[str] = []):
        self.distributedObject = None
        self.aiCharacter = None

        super().__init__(
            dcFileNames = dcFileNames,
            threadedNet = True,
            )

        tcpPort = p3d.ConfigVariableInt('server-port', 4400).get_value()
        hostname = p3d.ConfigVariableString('server-host', '127.0.0.1').get_value()

        self.url = p3d.URLSpec('http://{}:{}'.format(hostname, tcpPort))
        self.connect(
            [self.url],
            successCallback = self.connectSuccess,
            failureCallback = self.connectFailure,
            )

    def lostConnection(self):
        """ This should be overridden by a derived class to handle an
        unexpectedly lost connection to the gameserver. """
        # Handle the disconnection from the server.  This can be a reconnect,
        # simply exiting the application or anything else.
        exit()

    def connectFailure(self, statusCode, statusString):
        """ Something went wrong """
        # here we could create a reconnect task to try and connect again.
        exit()

    def connectSuccess(self):
        """ Successfully connected.  But we still can't really do
        anything until we've got the doID range. """

        # Make sure we have interest in the by the AIRepository defined
        # TimeManager zone, so we always see it even if we switch to
        # another zone.
        self.setInterestZones([1])

        # We must wait for the TimeManager to be fully created and
        # synced before we can enter another zone and wait for the
        # game object.  The uniqueName is important that we get the
        # correct, our sync message from the TimeManager and not
        # accidentaly a message from another client
        self.acceptOnce(self.uniqueName('gotTimeSync'), self.syncReady)

    def syncReady(self):
        """ Now we've got the TimeManager manifested, and we're in
        sync with the server time.  Now we can enter the world.  Check
        to see if we've received our doIdBase yet. """

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet
        if self.haveCreateAuthority():
            # we already have one
            self.gotCreateReady()
        else:
            # Not yet, keep waiting a bit longer.
            self.accept(self.uniqueName('createReady'), self.gotCreateReady)

    def gotCreateReady(self):
        """ Ready to enter the world.  Expand our interest to include
        any other zones """

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet
        if not self.haveCreateAuthority():
            # Not ready yet.
            return

        # we are ready now, so ignore further createReady events
        self.ignore(self.uniqueName('createReady'))

        self.join()

        print('Client Ready')
        base.messenger.send('client-ready')

    def join(self):
        """ Join a game/room/whatever """
        self.accept(self.uniqueName('AICharacterGenerated'), self.aiCharacterGenerated)

        # set our intersted zones to let the client see all distributed obects
        # in those zones
        self.setInterestZones([1, 2])

        base.messenger.send('client-joined')
        print('Joined')

    def aiCharacterGenerated(self, doId):
        print('AICharacter was generated')
        self.aiCharacter = self.doId2do[doId]
