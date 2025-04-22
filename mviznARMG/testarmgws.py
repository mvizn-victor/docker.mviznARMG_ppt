from armgws.armgws import sendjson
import sys
#def _sendjson(system,now,plc,imgfile):
import datetime
from Utils.helper import *
plc=readplc()
sendjson('TCDS','CNLSBF',datetime.now(),plc,'armgws/sample_data/HNCDS/2020-01-07_20-42-05_tl4xb_p.jpg')
import time
time.sleep(1)
sys.exit(0)

