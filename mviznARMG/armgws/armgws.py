#version:1
import time
from datetime import datetime
from threading import Thread
from armgws.event import Event

from websocket import create_connection
# uri = "ws://localhost:8765"
#uri = "ws://10.115.72.55:17001/websockets/vaReportServer/7409"
def sendjson(*args,**kwargs):
    thread = Thread(target=_sendjson,args=args,kwargs=kwargs,daemon=True)
    thread.start()
def _sendjson(system,camname,now,plc,imgfile):
    from config.config import wsuri, block, crane
    print("Sending JSON Event")
    time.sleep(0.5)
    pmnumber=plc.pmnumber
    contnum=plc.contnum
    row=plc.TrolleyPos
    slot=plc.GantryCurrSlot
    camimagelist = [(camname, imgfile)]
    newevent = Event(crane, pmnumber, now, 'ERROR', system, camimagelist, block, slot, row, contnum).getJSON()
    ws = create_connection(wsuri)
    ws.send(newevent)
    print("Sent Length", len(newevent))
    print("Receiving...")
    result =  ws.recv()
    print("'%s'" % result)
    ws.close()
    
def printandlog(*x,file=None,sep=None):
    thread = Thread(target=_printandlog, args=x, kwargs={'file':file,'sep':sep}, daemon=True)
    thread.start()


def _printandlog(*x,file=None,sep=None):
    print(*x,sep=sep)
    print(*x,file=file,sep=sep)    
