#version:1
def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

import cv2
from memcachehelper import memcacheRW as mcrw
import SharedArray as sa
def addnumber(number):
    pmnumbers=mcrw.raw_read('pmnumbers',set())
    pmnumbers.add(number)
    mcrw.raw_write('pmnumbers',pmnumbers)


import re
import sys
#from cabindetect import *

from datetime import datetime,timedelta
import numpy as np
import os
import glob
from config.config import * #import everything from Utils.helper too
from collections import defaultdict
from yolohelper import detect as YOLO
plc=readplc()
SIDE=plc.SIDE
assert SIDE in 'ls'
print(SIDE)
assert plc.JA
camraw=dict()
camnames=[f't{SIDE}4xf',f't{SIDE}20f']
for camname in camnames:
    camraw[camname]=sa.attach(f"shm://{camname}_raw")
pmnumber=plc.pmnumber

imshow=dict()
os.system('rm /dev/shm/*_pmnrsside')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_pmnrsside')
#from textdetect import *
Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/PMNRS/photologs/{JOBDATE}/{JOBTIME}'
PHOTOLOGRAWDIRNAME=f'/opt/captures/PMNRS/photologs_raw/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/PMNRS/logs/{JOBDATE}.txt'

#preload
from Utils.helper import dummyimage
results = YOLO.inferImg(np_image=dummyimage, thresh=0.2,
                            configPath="PMNRS/weights/PMNRS_lp.cfg",
                            weightPath="PMNRS/weights/PMNRS_lp.weights",
                            metaPath="PMNRS/weights/PMNRS_lp.data")

while True:
    if mcrw.raw_read('pmnumber_match',0):break
    mcrw.raw_write('pmnrsside_active',time.time())
    NOW = datetime.now()
    DATE = NOW.strftime('%Y-%m-%d')
    TIME = NOW.strftime('%H-%M-%S')
    T=time.time()
    for camname in camnames:
        frame=camraw[camname]
        frame_cpy=frame.copy()
        if 1:
            results = YOLO.inferImg(np_image=frame_cpy, thresh=0.2,
                                configPath="PMNRS/weights/PMNRS_lp.cfg",
                                weightPath="PMNRS/weights/PMNRS_lp.weights",
                                metaPath="PMNRS/weights/PMNRS_lp.data")
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            prob = result[1]
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = int(result[2][3] / 2)
            boxw = int(result[2][2] / 2)
            x1 = xc - boxw
            y1 = yc - boxh
            x2 = xc + boxw
            y2 = yc + boxh
            cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (66, 66, 244), 3)
            if mcrw.raw_read('pmnrstop_active',0)==0:
                text,prob=OCR(frame[y1:y2,x1:x2])
                pmnumber_read=text
                if pmnumber_read==pmnumber and pmnumber_read!='':
                    pmnumber_match=1
                    mcrw.raw_write('pmnumber_match',time.time())
                    mcrw.raw_write('pmnumber_read',pmnumber_read)
                    addnumber(pmnumber_read)
        assignimage(imshow[camname], frame_cpy)
        if len(results)>0:
            makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}.jpg', frame)
            #added annotation 2021-04-15
            makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}.jpg', frame_cpy)

    Telapse=time.time()-T
    print(Telapse)
    time.sleep(max(0.2-Telapse,0))
