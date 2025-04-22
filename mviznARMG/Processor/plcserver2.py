from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ServerFactory
import pickle
import struct
import glob
plcfiles=sorted(glob.glob('sample/tcds/plcin/*.dat'))
plcidx=0
plcN=len(plcfiles)
class ClientLineReceiver(LineOnlyReceiver):
    def __init__(self):
        pass
    def dataReceived(self, data):
        global dummybytes,plcidx
        #print('receiveddata',data)
        try:
            dummybytes=open(plcfiles[plcidx],'rb').read()
            print(dummybytes)
        except:
            raise
        self.sendLine(dummybytes[:78])
        plcidx=(plcidx+1)%plcN
        print('plcidx:',plcidx)
    def lineReceived(self, line):
        print('receivedline',line)
        self.sendLine(dummybytes)

class RespFactory(ServerFactory):
    protocol = ClientLineReceiver


if __name__ == '__main__':
    reactor.listenTCP(2009, RespFactory(), interface='0.0.0.0')
    reactor.run()
