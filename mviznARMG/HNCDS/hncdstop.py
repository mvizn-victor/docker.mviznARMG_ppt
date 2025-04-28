#version:id22
#gd21 1FPS
#gh22
#  enablebit = stopprocessing
#  for each camera, maintain hitlist. if hitlist has 2 or more elements then update plc
#gj23
#  only p above top half of cabin considered h (reduce false negative of driver violation unlock front twistlock)
#hd23
#  'p' not in violations don't send to CIU
#  p in zoomin considered moving
#he02
#  whenever log in moving, send to CIU
#hf14
#  snapshot when at row 1 for seaside, row 10 for landside

from shapely.geometry import Polygon,box

def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

from armgws.armgws import sendjson
from collections import defaultdict
reported=defaultdict(int)

athresh=0
cthresh=0
hthresh=0
pthresh=0.3

from datetime import datetime, timedelta
import time
from memcachehelper import memcacheRW as mcrw
import cv2
import os

import SharedArray as sa
from config.config import *
from Utils.helper import procimage

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

#hf14
class C__risechecker:
    def __init__(self):
        self.curr=False
        self.last=False
    def update(self,cond):
        self.curr=cond
        ret = self.curr and not self.last
        self.last=self.curr
        return ret
d__risechecker={}
for camname in camnames:
    d__risechecker[camname]=C__risechecker()

##begin gh22 1##
def updateandqueryhitlist(camname,x,y):
    found=0
    for x1,y1 in hitlist[camname]:
        if ((x1-x)**2+(y1-y)**2)**.5<hitlistd:
            found=1
    if not found:
        hitlist[camname].append((x,y))
    return len(hitlist[camname])
hitlist=dict()
hitlistd=50
for camname in camnames:
    hitlist[camname]=[]
##end gh22 1##
imshow['ovxscabin']=createShm(f'ovxscabin_hncdstop')
Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
INCEPTIONDIRNAME=f'/opt/captures/HNCDS/photologs_raw/{JOBDATE}/inception'
PHOTOLOGDIRNAME=f'/opt/captures/HNCDS/photologs/{JOBDATE}/{JOBTIME}'
PHOTOLOGRAWDIRNAME=f'/opt/captures/HNCDS/photologs_raw/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/HNCDS/logs/{JOBDATE}.txt'
lastT1 = 0
detectiongrid=dict()
ignoretime=0
for camname in camnames:
    detectiongrid[camname]=np.zeros((73,129),dtype=np.int)
lastHNCDS_OpsAck = 0
while True:
    T=time.time()    
    NOW = datetime.fromtimestamp(time.time()//1*1)
    DATE = NOW.strftime('%Y-%m-%d')
    TIME = NOW.strftime('%H-%M-%S')
    plc = readplc()
    if not lastHNCDS_OpsAck and plc.HNCDS_OpsAck:
        ignoretime=time.time()
    lastHNCDS_OpsAck = plc.HNCDS_OpsAck
    print(datetime.now(),"byte78",bin(plc.data[78])) 
    HNCDS_StopProcessing = plc.HNCDS_Enable #repurposed
    if HNCDS_StopProcessing:
        mcrw.raw_write('hncds_processing',0)
        time.sleep(0.25)
        continue
    else:
        mcrw.raw_write('hncds_processing',time.time())
    
    for camname in camnames:
        hasmoving=0 ## gh22
        mcrw.raw_write('hncdstop_active', time.time())
        frame = camraw[camname].copy()
        frame_cpy = frame.copy()
        if plc.GantryCurrSlot==plc.GantryTargetSlot:        
            results = procimage('hncdstopyolo',frame)
            #ignore detection if not yet reach destination
            va = 0
            vh = 0
            vp = 0
            def getcabins():
                cabins=[]
                for result in results:
                    name=result[0]
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
                return cabins
            cabins=getcabins()
            #left most for land side
            #right most for sea side
            cabins.sort()
            if SIDE=='l':
                cabins=cabins[:1]
            elif SIDE=='s':
                cabins=cabins[-1:]
            if camname in ['ovls','ovss']:
                for (x1_,y1_,x2_,y2_) in cabins:
                    w_=x2_-x1_
                    cv2.line(frame_cpy,(x1_-w_,0),(x1_-w_,720),(0,255,0),3)
                    cv2.line(frame_cpy,(x2_+w_,0),(x2_+w_,720),(0,255,0),3)
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
                #if name == 'p' and camname not in ['ovls','ovss']:
                if name == 'p':
                    #ignore static object detected before
                    if detectiongrid[camname][yc//10,xc//10]==0:
                        detectiongrid[camname][yc//10,xc//10]=int(time.time())
                    if detectiongrid[camname][yc//10,xc//10]<ignoretime:
                        print(camname,xc,yc,'ignore due to opsack')
                        continue
                if name == 'p':
                    makedirsimwrite(f'{INCEPTIONDIRNAME}/{DATE}_{TIME}_{camname}.jpg', frame[max(0, y1):y2, max(0, x1):x2])
                if name=='p' and prob>=pthresh and procimage('hncdsinception',frame[max(0, y1):y2, max(0, x1):x2])[0] != 'p':
                    continue
                xnearcabin=False
                if name == 'p' and prob>=pthresh:
                    #if overlap with cabin name='h'
                    overlapcabin=False                    
                    for (x1_,y1_,x2_,y2_) in cabins:
                        eps=1 #(x2_-x1_)/10
                        #door is on cabin right, human detected near right side of cabin considered as head
                        #gj23                                                     
                        #if box(x2_,y1_,x2_+eps,y2_).intersects(box(x1,y1,x2,y2)):
                        if box(x2_,y1_,x2_+eps,(y1_+y2_)//2).intersects(box(x1,y1,x2,y2)):                          
                            overlapcabin=True
                            print('overlapcabin')
                    if overlapcabin:name='h' #ignored for unzoomed 
                    else:
                        for (x1_,y1_,x2_,y2_) in cabins:
                            w_=x2_-x1_
                            if box(x1_-w_,0,x2_+w_,1280).intersects(box(x1,y1,x2,y2)):
                                xnearcabin=True
                                print('xnearcabin')
                if camname in ['ovls','ovss']:
                    if name in ['a','c','h'] or name=='p' and not xnearcabin:
                        #ignore a,c,h for unzoomed ovxs and p if not nearcabin
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
                    ##begin gh22 3
                    hitcount=updateandqueryhitlist(camname,xc,yc)
                    if hitcount>=2:
                        mcrw.raw_write('last_hncds_p', time.time())
                        hasmoving=1
                    ##end gh22 3
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
                    cv2.putText(frame_cpy, f'{name}:{prob:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 0, 0), 2)
            violations = vp * 'p' + va * 'a' + vh * 'h'
            if len(violations) > 0:
                #begin gh22 3
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame_cpy)
                if not reported[DATE,TIME,camname,violations] and hasmoving and 'p' in violations:
                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/moving/{DATE}_{TIME}_{camname}_{violations}.jpg', frame_cpy)
                    sendjson('HNCDS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg')
                    reported[DATE,TIME,camname,violations]=1

                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame)
                printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, violations, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                #begin gh22 3
            
            #hf14
            snapshotcond=d__risechecker[camname].update(abs(plc.TrolleyPos-plc.SIDEINFO)<=1)
            print(camname,('plc.TrolleyPos','plc.SIDEINFO'),'=',(plc.TrolleyPos,plc.SIDEINFO),snapshotcond)
            if snapshotcond:
                print(camname,'snapshot!')
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot/{DATE}_{TIME}_{camname}.jpg', frame)
                    
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
                    results = procimage('hncdstopyolo',framecabin)
                    if 0:
                        results = YOLO.inferImg(np_image=framecabin, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDS.cfg",
                                    weightPath="HNCDS/weights/HNCDS.weights",
                                    metaPath="HNCDS/weights/HNCDS.data")
                    print(cabini,results)
                    def getcabins():                                
                        cabins=[]
                        for result in results:
                            name=result[0]
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
                        return cabins
                    cabins_=getcabins()
                    for result in results:
                        name=result[0]
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
                        if name == 'p':
                            makedirsimwrite(f'{INCEPTIONDIRNAME}/{DATE}_{TIME}_{camname}.jpg', framecabin[max(0, y1):y2, max(0, x1):x2])
                        if name == 'p' and prob >= pthresh and procimage('hncdsinception',framecabin[max(0, y1):y2, max(0, x1):x2])[0] != 'p':
                           continue
                        if name == 'p' and prob>=pthresh:
                            #if overlap with cabin name='h'
                            overlapcabin=False
                            for (x1_,y1_,x2_,y2_) in cabins_:
                                eps=1 #(x2_-x1_)/10
                                #door is on cabin right, human detected near right side of cabin considered as head
                                #if box(x2_,y1_,x2_+eps,y2_).intersects(box(x1,y1,x2,y2)):
                                #gj23
                                if box(x2_,y1_,x2_+eps,(y1_+y2_)//2).intersects(box(x1,y1,x2,y2)):
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
                            cv2.putText(framecabin_cpy, f'{name}:{prob:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (255, 0, 0), 2)
                    violations = vp * 'p' + va * 'a' + vh * 'h'
                    if len(violations) > 0:
                        #violation around each cabin
                        makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg', framecabin_cpy)
                        if not reported[DATE,TIME,camname,cabini] and 'p' in violations:
                            makedirsimwrite(f'{PHOTOLOGDIRNAME}/moving/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg', framecabin_cpy)
                            sendjson('HNCDS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg')
                            reported[DATE,TIME,camname,cabini]=1
                        makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}_cabin{cabini}_{violations}.jpg', framecabin)
                        printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, violations, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                    
                    #hf14
                    snapshotcond=d__risechecker[camname].update(abs(plc.TrolleyPos-plc.SIDEINFO)<=1)
                    print(camname,('plc.TrolleyPos','plc.SIDEINFO'),'=',(plc.TrolleyPos,plc.SIDEINFO),snapshotcond)
                    if snapshotcond:
                        print(camname,'snapshot!')
                        makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot/{DATE}_{TIME}_{camname}_cabin{cabini}.jpg', frame_cpy)
                        makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot/{DATE}_{TIME}_{camname}_cabin{cabini}.jpg', frame)
                                              
        if camname in ['ovls','ovss']:
            try:
                assignscaleimage(imshow['ovxscabin'],framecabin_cpy)
            except:
                pass
        #except:
        assignimage(imshow[camname],frame_cpy)
    Telapse=time.time()-T
    print(Telapse)
    #time.sleep(max(0.5-Telapse,0))
    time.sleep(max(0.95-Telapse,0))
mcrw.raw_write('hncds_processing',0)    
