import time
from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory
import pickle
import struct
dummybytes=open('plc.dat','rb')

class ClientLineReceiver(LineOnlyReceiver):
    def __init__(self):
        pass
    def dataReceived(self, data):
        #print('receiveddata',data)
        self.sendLine(dummybytes[:78])
    def lineReceived(self, line):
        print('receivedline',line)
        self.sendLine(dummybytes)

class RespFactory(ServerFactory):
    protocol = ClientLineReceiver


if __name__ == '__main__':
    reactor.listenTCP(2009, RespFactory(), interface='0.0.0.0')
    reactor.run()
