athresh=0
cthresh=0
hthresh=0
pthresh=0

from datetime import datetime, timedelta
import time
from memcachehelper import memcacheRW as mcrw
import cv2
import os
from yolohelper import detect as YOLO
import SharedArray as sa
from shapely.geometry import Polygon,box
from config.config import *
plc=readplc()
SIDE=plc.SIDE
camraw = dict()
yoloframe = dict()
camnames= [f'ov{SIDE}s', f'pmn{SIDE}s']
for camname in camnames:
    camraw[camname] = sa.attach(f"shm://{camname}_raw")
for camname in camnames:
    yoloframe[camname] = sa.attach(f"shm://{camname}_yoloframe")

imshow=dict()
os.system('rm /dev/shm/*_hncdstop')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_hncdstop')

Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/HNCDS/photologs/{JOBDATE}/{JOBTIME}'
PHOTOLOGRAWDIRNAME=f'/opt/captures/HNCDS/photologs_raw/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/HNCDS/logs/{JOBDATE}.txt'

lastT1 = 0
while True:
    T=time.time()
    mcrw.raw_write('hncdstop_active', time.time())
    NOW = datetime.fromtimestamp(time.time()//1*1)
    DATE = NOW.strftime('%Y-%m-%d')
    TIME = NOW.strftime('%H-%M-%S')
    plc = readplc()
    for camname in camnames:  
        frame = camraw[camname].copy()
        frame_cpy = frame.copy()
        framecabin_cpy=None
        if 'ovtr' in camname:
            if abs(plc.TrolleyPos-plc.SIDEINFO)>1:
                #ignore ovtr cameras when trolley not in position
                continue
        results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                configPath="HNCDS/weights/HNCDS.cfg",
                                weightPath="HNCDS/weights/HNCDS.weights",
                                metaPath="HNCDS/weights/HNCDS.data")

        if 'ovtr' not in camname:
            mcrw.raw_write(f'{camname}_yolo',[results,time.time()])
            assignimage(yoloframe[camname],frame)
            #saved for pmnrs
        if plc.GantryCurrSlot==plc.GantryTargetSlot:        
            #ignore detection if not yet reach destination
            va = 0
            vh = 0
            vp = 0
            def getcabins():
                cabins=[]
                for result in results:
                    name=results[0]
                    if type(name) == bytes:
                        name = name.decode('utf8')
                    if name=='t':
                        xc = int(result[2][0])
                        yc = int(result[2][1])
                        boxh = int(result[2][3] / 2)
                        boxw = int(result[2][2] / 2)
                        x1 = xc - boxw
                        y1 = yc - boxh
                        x2 = xc + boxw
                        y2 = yc + boxh
                        cabins.append([x1,y1,x2,y2])
                       
            cabins=getcabins()
            for result in results:
                name = result[0]
                if type(name) == bytes:
                    name = name.decode('utf8')
                    
                prob = result[1]
                xc = int(result[2][0])
                yc = int(result[2][1])
                boxh = int(result[2][3] / 2)
                boxw = int(result[2][2] / 2)
                SIZE = max(boxw, boxh) * 2
                x1 = xc - boxw
                y1 = yc - boxh
                x2 = xc + boxw
                y2 = yc + boxh
                
                if name == 'p' and prob>=pthresh:
                    #if overlap with cabin name='h'
                    overlapcabin=False
                    for (x1_,y1_,x2_,y2_) in cabins:
                        eps=(x2_-x1_)/10
                        #door is on cabin right, human detected near right side of cabin considered as head
                        if box(x2_,y1_,x2_+eps,y2_).intersects(box(x1,y1,x2,y2))
                            overlapcabin=True
                            print('overlapcabin')
                    if overlapcabin:name='h' #ignored for unzoomed 
                    else:name='p'

                if camname in ['ovls','ovss'] and name in ['a','c','h']:
                    #ignore a,c,h for unzoomed ovxs
                    continue

                if name == 'a' and prob>=athresh or name == 'c' and prob>=cthresh:
                    va = 1
                    todraw=1
                    mcrw.raw_write('last_hncds_a', time.time())
                elif name == 'h' and prob>=hthresh:
                    vh = 1
                    mcrw.raw_write('last_hncds_h', time.time())
                    todraw=1
                elif name == 'p' and prob>=pthresh:
                    vp = 1
                    mcrw.raw_write('last_hncds_p', time.time())
                    todraw=1
                elif name == 't':
                    todraw=1
                else:
                    todraw=0
                if name == 'a' or name == 'c': color = (255, 0, 0)
                if name == 'h': color = (0, 255, 0)
                if name == 'p': color = (0, 0, 255)
                if name == 't': color = (255,255,0)
                if todraw:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame_cpy, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 0, 0), 2)
            violations = vp * 'p' + va * 'a' + vh * 'h'
            if len(violations) > 0:
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame)
                printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, violations, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
            #above is only human detection from uncropped ovxs and all detections from pmnxs
            #below is cropped cameras only
            if camname in ['ovls','ovss']:
                for cabini,cabin in enumerate(cabins):
                    va=0
                    vh=0
                    vp=0                
                    x1,y1,x2,y2=cabin
                    w=x2-x1
                    h=y2-y1
                    minx=max(0,int(x1-w))                
                    maxx=int(x2+w)
                    miny=max(0,int(y1-h))
                    maxy=int(y2+h)
                    framecabin=frame[miny:maxy,minx:maxx]
                    framecabin_cpy=framecabin.copy()
                    results = YOLO.inferImg(np_image=framecabin, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDS.cfg",
                                    weightPath="HNCDS/weights/HNCDS.weights",
                                    metaPath="HNCDS/weights/HNCDS.data")                                    
                                    
                    def getcabins():                                
                        cabins=[]
                        for result in results:
                            name=results[0]
                            if type(name) == bytes:
                                name = name.decode('utf8')
                            if name=='t':
                                xc = int(result[2][0])
                                yc = int(result[2][1])
                                boxh = int(result[2][3] / 2)
                                boxw = int(result[2][2] / 2)
                                x1 = xc - boxw
                                y1 = yc - boxh
                                x2 = xc + boxw
                                y2 = yc + boxh
                                cabins.append([x1,y1,x2,y2])
                    cabins_=getcabins()
                    for result in results:
                        name=results[0]
                        if type(name) == bytes:
                            name = name.decode('utf8')                    
                        prob = result[1]
                        xc = int(result[2][0])
                        yc = int(result[2][1])
                        boxh = int(result[2][3] / 2)
                        boxw = int(result[2][2] / 2)
                        SIZE = max(boxw, boxh) * 2
                        x1 = xc - boxw
                        y1 = yc - boxh
                        x2 = xc + boxw
                        y2 = yc + boxh
                        
                        if name == 'p' and prob>=pthresh:
                            #if overlap with cabin name='h'
                            overlapcabin=False
                            for (x1_,y1_,x2_,y2_) in cabins_:
                                eps=(x2_-x1_)/10
                                #door is on cabin right, human detected near right side of cabin considered as head
                                if box(x2_,y1_,x2_+eps,y2_).intersects(box(x1,y1,x2,y2))
                                    overlapcabin=True
                                    print('overlapcabin')
                            if overlapcabin:name='h'
                            else:name='p'

                        if name == 'a' and prob>=athresh or name == 'c' and prob>=cthresh:
                            va = 1
                            todraw=1
                            mcrw.raw_write('last_hncds_a', time.time())
                        elif name == 'h' and prob>=hthresh:
                            vh = 1
                            mcrw.raw_write('last_hncds_h', time.time())
                            todraw=1
                        elif name == 'p' and prob>=pthresh:
                            vp = 1
                            mcrw.raw_write('last_hncds_p', time.time())
                            todraw=1
                        elif name == 't':
                            todraw=1
                        else:
                            todraw=0
                        if name == 'a' or name == 'c': color = (255, 0, 0)
                        if name == 'h': color = (0, 255, 0)
                        if name == 'p': color = (0, 0, 255)
                        if name == 't': color = (255,255,0)
                        if todraw:
                            cv2.rectangle(framecabin_cpy, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(framecabin_cpy, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                    (255, 0, 0), 2)
                    violations = vp * 'p' + va * 'a' + vh * 'h'
                    if False and len(violations) > 0:
                        #violation around each cabin
                        makedirsimwrite(f'{PHOTOLOGDIRNAME}/test/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg', framecabin_cpy)
                        makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/test/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg', framecabin)
                        #printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, violations, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
        try:
            assignscaleimage(imshow[camname],framecabin_cpy)
        except:
            assignimage(imshow[camname],frame_cpy)
        Telapse=time.time()-T
        time.sleep(max(0.5-Telapse,0))
