
from datetime import datetime
from event import Event
from config.config import wsuri, crane
now = datetime.now()

jsonevents = []
camimagelist = [('OVLS', 'armgws/sample_data/HNCDS/2020-01-07_20-42-05_tl4xb_p.jpg')]
newevent = Event('7110', 'XE1446E', now, 'ERROR', 'HNCDS', camimagelist, 10, 2, 3, 'TEMU 3444621')
jsonevents.append(newevent)

camimagelist = [('TL20B', 'armgws/sample_data/CLPS/2020-01-13_14-43-36_tl20b.jpg')]
newevent = Event('7110', 'XB9535U', now, 'ERROR', 'CLPS', camimagelist, 11, 1, 1, 'BEAU 2379502')
jsonevents.append(newevent)

camimagelist = [('TL20B', 'armgws/sample_data/TCDS/2020-01-07_14-13-16_tl20b_4.jpg')]
newevent = Event('7110', 'PPM8342', now, 'ERROR', 'TCDS', camimagelist, 9, 1, 1, 'APRU 5793114')
jsonevents.append(newevent)

jsonevent = jsonevents[0].getJSON()
#print(jsonevent)
#exit(0)
from websocket import create_connection
# uri = "ws://localhost:8765"
#uri = "ws://10.115.72.55:17001/websockets/vaReportServer/7409"

ws = create_connection(wsuri)
print("Sending JSON Event")
ws.send(jsonevent)
print("Sent Length", len(jsonevent))
print("Receiving...")
result =  ws.recv()
print("'%s'" % result)
ws.close()
