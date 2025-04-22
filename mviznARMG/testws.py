from armgws.armgws import _sendjson
from datetime import datetime
class G:
    pass
plc=G()
plc.pmnumber='XD1234A'
plc.contnum='somecnt'
plc.TrolleyPos=0
plc.GantryCurrSlot=0


_sendjson('TCDS','testcam',datetime.now(),plc,f'armgws/sample_data/TCDS/2020-01-07_14-13-16_tl20b_4.jpg')
