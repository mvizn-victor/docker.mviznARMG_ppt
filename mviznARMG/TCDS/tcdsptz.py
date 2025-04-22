#version:fi30
#!/usr/bin/env python
def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

import os
import sys
if os.path.exists('config/tcdstx'):
    print('running degraded TCDS, not panning')
    sys.exit(0)

nighttiltup=False
from config.config import *
import json
import socket
import struct
import binascii
import random
import time
from datetime import date, datetime
import numpy as np
import shutil
import os
from memcachehelper import memcacheRW as mcrw
allfiles = """cnlsbb45-1.txt
cnlsbb45-2.txt
cnlsbf45-1.txt
cnlsbf45-2.txt
cnlsbc45.txt
cnlsbb40-1.txt
cnlsbb40-2.txt
cnlsbf40-1.txt
cnlsbf40-2.txt
cnlsbc40.txt
cnlsbb20.txt
cnlsbf20.txt
cnlsbc20.txt
cnssbb45-1.txt
cnssbb45-2.txt
cnssbf45-1.txt
cnssbf45-2.txt
cnssbc45.txt
cnssbb40-1.txt
cnssbb40-2.txt
cnssbf40-1.txt
cnssbf40-2.txt
cnssbc40.txt
cnssbb20.txt
cnssbf20.txt
cnssbc20.txt
""".strip().split()
allfilesexist = True
for f in allfiles:
    if not os.path.isfile(f'config/tcds/{f}'):
        allfilesexist = False
        print(f, 'does not exists')
    else:
        print(f, 'exists')
if not allfilesexist:
    raise Exception('not all config files exist')
if 1:
    all1files = """cnlsbb40-1.txt
    cnlsbb45-1.txt
    cnlsbf40-1.txt
    cnlsbf45-1.txt
    cnssbb40-1.txt
    cnssbb45-1.txt
    cnssbf40-1.txt
    cnssbf45-1.txt""".strip().split()
    differror = 0
    for f1 in all1files:
        f2 = f1.replace('-1', '-2')
        if os.system(f'diff config/tcds/{f1} config/tcds/{f2} >/dev/null 2>&1') == 0:
            diff = 0
        else:
            diff = 1
        if f1 in ['cnlsbf45-1.txt', 'cnssbf45-1.txt'] and not diff:
            print(f1, f2, 'should be different')
            differror = 1
        if f1 not in ['cnlsbf45-1.txt', 'cnssbf45-1.txt'] and diff:
            print(f1, f2, 'should not be different')
            differror = 1
    if differror:
        raise Exception('diff test fail')
    else:
        print('diff test pass')

heightbuffer = 200
lastHoistPos = 0
frame = 0
speed = 0
STATEBF = 'HOME'
STATEC = 'HOME'
mcrw.raw_write('tcds_statebf', 0)
mcrw.raw_write('tcds_statec', 0)
while True:    
    T1 = time.time()
    plc=readplc()
    JA = plc.JA
    TLOCK = plc.TLOCK
    MI = plc.MI
    CNRSCompleted = plc.CNRSCompleted
    HoistPos = plc.HoistPos
    SIDEINFO=plc.SIDEINFO
    SIDE=plc.SIDE
    JOBTYPE=plc.JOBTYPE
    containerpos=plc.containerpos
    size=plc.size
    speed=plc.speed
    externalpm=plc.externalpm
    if frame % 10 == 0:
        print('HERE:', 'JT:', JOBTYPE, 'JA:', JA * 1, 'MI:', MI * 1, 'CNRS:', CNRSCompleted * 1,'ext:',externalpm*1,
              'H:', HoistPos, 'CP:', containerpos, 'TL:', TLOCK * 1, 'SIDE:', SIDEINFO, SIDE, 'size:', size, 'speed:',
              speed, STATEBF, STATEC)
    estHoistPos = plc.getEstHoistPos()
    # SIDE='l'
    # SIDE='s'

    if SIDE in 'ls':  # LANDSIDE AND SEASIDE
        heighttriggerbf45enter = 11000
        try:
            panoffset=int(open(f'config/tcds/panoffset_cn{SIDE}sbf.txt').read())
        except:
            panoffset=0
        heighttriggerbf45pan = 11400+panoffset
        heighttriggerbf45exit = 12200
        heighttriggerc45enter = 8430
        heighttriggerc45exit = 11000
    NOW = datetime.now()
    if JOBTYPE=='OFFLOADING' and SIDE in 'ls':  # OFFLOADING and SIDE in 'ls':
        if JA and CNRSCompleted and not MI:
            if size == 45 or size == 40 or size == 20:
                if STATEBF == 'HOME' and TLOCK and speed > 0 and 6000 < estHoistPos < min(heighttriggerbf45exit,heighttriggerc45exit) + heightbuffer:
                    print('BF:HOME->READY')
                    print('C:HOME->READY')
                    for camname in [f'cn{SIDE}sbf', f'cn{SIDE}sbb']:
                        try:
                            cam = eval(camname)
                            if nighttiltup and (18<=datetime.now().hour<24 or 0<=datetime.now().hour<8) and (camname,size)!=(f'cn{SIDE}sbf',45):
                                if size in [40, 45]:
                                    cam.loadpostxt(f'config/tcds/{camname}{size}-1.txt',tiltoffset=6)
                                else:
                                    cam.loadpostxt(f'config/tcds/{camname}{size}.txt',tiltoffset=6)
                            else:
                                if size in [40, 45]:
                                    cam.loadpostxt(f'config/tcds/{camname}{size}-1.txt')
                                else:
                                    cam.loadpostxt(f'config/tcds/{camname}{size}.txt')
                        except:
                            pass

                    for camname in [f'cn{SIDE}sbc']:
                        try:
                            cam = eval(camname)
                            cam.loadpostxt(f'config/tcds/{camname}{size}.txt')
                        except:
                            pass
                    STATEBF = 'READY'
                    STATEC = 'READY'
                    startrecord = time.time()
                    # startrecordint=int(startrecord*1e6)
                    startrecordint = datetime.fromtimestamp(startrecord).strftime("%Y%m%d-%H%M%S")
                    #mcrw.raw_write('tcds_statebf', 1)
                    #mcrw.raw_write('tcds_statec', 1)
                    Tpan1=time.time()
                    
                if STATEBF == 'READY' and mcrw.raw_read('tcds_statebf',0)==0 and time.time()-Tpan1>=0.5:
                    #wait .5s for camera to pan finish
                    mcrw.raw_write('tcds_statebf', 1)
                if STATEC == 'READY' and mcrw.raw_read('tcds_statec',0)==0 and time.time()-Tpan1>=0:
                    #wait 0s for camera to pan finish
                    mcrw.raw_write('tcds_statec', 1)

                if STATEBF == 'READY' and estHoistPos >= heighttriggerbf45enter - heightbuffer:
                    print('bf:READY->RECORD1')
                    STATEBF = 'RECORD1'
                    mcrw.raw_write('tcds_statebf',1)
                elif STATEBF == 'RECORD1' and estHoistPos >= heighttriggerbf45pan:
                    print('bf:RECORD1->RECORD2')
                    if size in [40,45]:
                        for camname in [f'cn{SIDE}sbf', f'cn{SIDE}sbb']:                        
                            try:
                                cam = eval(camname)
                                if nighttiltup and (18<=datetime.now().hour<24 or 0<=datetime.now().hour<8) and (camname,size)!=(f'cn{SIDE}sbf',45):
                                    cam.loadpostxt(f'config/tcds/{camname}{size}-2.txt',tiltoffset=6)
                                else:
                                    cam.loadpostxt(f'config/tcds/{camname}{size}-2.txt')
                            except:
                                pass
                    STATEBF = 'RECORD2'
                    mcrw.raw_write('tcds_statebf', 2)
                elif STATEBF == 'RECORD2' and estHoistPos >= heighttriggerbf45exit + heightbuffer:
                    print('bf:RECORD2->HOME')
                    STATEBF = 'HOME'
                    mcrw.raw_write('tcds_statebf', 3)
                if STATEC == 'READY' and estHoistPos >= heighttriggerc45enter - heightbuffer:
                    print('c:READY->RECORD')
                    STATEC = 'RECORD'
                    mcrw.raw_write('tcds_statec', 1)
                elif STATEC == 'RECORD' and estHoistPos >= heighttriggerc45exit + heightbuffer:
                    print('c:RECORD->HOME')
                    STATEC = 'HOME'
                    mcrw.raw_write('tcds_statec', 3)
        else:
            if STATEBF != 'HOME':
                print(f'bf:{STATEBF}->HOME')
                STATEBF = 'HOME'
                mcrw.raw_write('tcds_statebf', 3)
            if STATEC != 'HOME':
                print(f'c:{STATEC}->HOME')
                STATEC = 'HOME'
                mcrw.raw_write('tcds_statec', 3)
    if speed < 0:
        if STATEBF != 'HOME':
            print(f'bf:{STATEBF}->HOME')
            STATEBF = 'HOME'
            mcrw.raw_write('tcds_statebf', 3)           
        if STATEC != 'HOME':
            print(f'c:{STATEC}->HOME')
            STATEC = 'HOME'
            mcrw.raw_write('tcds_statec', 3)
    if mcrw.raw_read('tcds_statebf',0)==3:
        time.sleep(1)
        mcrw.raw_write('tcds_statebf', 4)
        time.sleep(3)
        raise Exception('END')
    frame += 1
    Telapse = time.time() - T1
    # print(Telapse)
    #print(plc.getEstHoistPos())
    time.sleep(max(0.05 - Telapse, 0))
