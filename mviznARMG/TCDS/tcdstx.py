#version:id22
#id22:
# always use cv2dnn

builtinprint=print
def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    builtinprint(*x,**kw)

from armgws.armgws import sendjson

hitsy_diffthresh=50
minhits=1 #corner detection minimum hits for 45feet corner detection
#subyolo sum(score>0)>=1 in minhits
lognegative=True
PAN_DELAY=0.5
import cv2
if 1: #id22
    from Utils.cv2dnn import YOLO as CV2YOLO
    class YOLOdarknet:
        cv2yolo=None
        def inferImg(self,weightPath,thresh,np_image=None,**kwargs):
            if np_image is None:
                np_image=np.zeros((3,3,3),dtype=np.uint8)
            if self.cv2yolo is None:
                self.cv2yolo=CV2YOLO(weightPath)
            return self.cv2yolo.inferold(np_image,thresh=thresh)
    YOLO=YOLOdarknet()
    YOLO2=YOLOdarknet()
else:
    from yolohelper import detect as YOLO
    from yolohelper import detect2 as YOLO2
import SharedArray as sa
import glob
import re
import numpy as np
from config.config import *
from config.cornerx import cornerx
if 0:
    def print(*x,**kw):
        kw['file']=open('/tmp/tcds.log','a')
        __builtins__.print(*x,**kw)
print('start',time.time())


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

deploy=1
if deploy:
    os.environ['CUDA_VISIBLE_DEVICES']='1'


plc=readplc()
SIDE=plc.SIDE
SIZE=plc.size
if SIZE>=40:
    SIZEX='4x'
else:
    SIZEX='20'

mcrw.raw_write('tcds_corner1',0)
mcrw.raw_write('tcds_corner2',0)
mcrw.raw_write('tcds_corner3',0)
mcrw.raw_write('tcds_corner4',0)
mcrw.raw_write('tcds_corner5',0)
mcrw.raw_write('tcds_corner6',0)
mcrw.raw_write('tcds_corner7',0)
mcrw.raw_write('tcds_corner8',0)
mcrw.raw_write('tcds_cf',0)
mcrw.raw_write('tcds_cb',0)
mcrw.raw_write('tcds_cc',0)
mcrw.raw_write('tcds_tf',0)
mcrw.raw_write('tcds_tb',0)

cornermap=dict()
cornermap[20,'cnlsbf']=(2,3)
cornermap[20,'cnlsbb']=(4,1)
cornermap[20,'cnlsbc']=(4,4) #point to back
cornermap[20,'tl20f']=(3,3)
cornermap[20,'tl20b']=(4,4)
cornermap[20,'cnssbf']=(2,3)
cornermap[20,'cnssbb']=(4,1)
cornermap[20,'cnssbc']=(2,2) #point to front
cornermap[20,'ts20f']=(2,2)
cornermap[20,'ts20b']=(1,1)


cornermap[40,'cnlsbf']=(2,3)
cornermap[40,'cnlsbb']=(1,1)
cornermap[40,'cnlsbc']=(4,4) #point to back
cornermap[40,'tl4xf']=(3,3)
cornermap[40,'tl4xb']=(4,4)
cornermap[40,'cnssbf']=(2,3)
cornermap[40,'cnssbb']=(4,1)
cornermap[40,'cnssbc']=(1,1) #point to back
cornermap[40,'ts4xf']=(2,2)
cornermap[40,'ts4xb']=(1,1)

cornermap[45,'cnlsbf',1]=(2,6)
cornermap[45,'cnlsbf',2]=(7,3)
cornermap[45,'cnlsbb']=(5,1)
cornermap[45,'cnlsbc']=(8,4) #point to back
cornermap[45,'tl4xf']=(3,7)
cornermap[45,'tl4xb']=(8,4)
cornermap[45,'cnssbf',1]=(7,3)
cornermap[45,'cnssbf',2]=(2,6)
cornermap[45,'cnssbb']=(4,8)
cornermap[45,'cnssbc']=(1,5) #point to back
cornermap[45,'ts4xf']=(6,2)
cornermap[45,'ts4xb']=(1,5)

camnames=[f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b']
#camnames=[f'cn{SIDE}sbf',f'cn{SIDE}sbb',f'cn{SIDE}sbc']
cam=dict()
camrawlastT=dict()
camscores=dict()
from collections import deque,defaultdict
detected=dict()
storedetection=dict()
negdetected=dict()
negstoredetection=dict()

def insertscore(bindict,p,score):
    x,y=p
    inserted=False
    for k in bindict:
        if abs(x-k)<=bindist:
            bindict[k].append((score,p))
            inserted=True
            break
    if not inserted:
        bindict[x].append((score,p))

def isnewx(bindict,x):
    inserted=False
    for k in bindict:
        if abs(x-k)<=bindist:
            return False
    return True
    
bindist=100
for camname in camnames:
    cam[camname]=sa.attach(f'shm://{camname}_raw')
    camrawlastT[camname]=0
    camscores[camname]=defaultdict(list)
    storedetection[camname]=dict()
    negstoredetection[camname]=dict()    
    for corner in range(1,9):
        detected[camname,corner]=False
        negdetected[camname,corner]=False

os.system('rm /dev/shm/*_tcds')
imshow=dict()
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_tcds')

Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/TCDS/photologs/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/TCDS/logs/{JOBDATE}.txt'
PAN_WAIT=0

lasttcds_statebf=0
#with tf.Session(config=tfconfig, graph=infer.graph) as sess:
#    infer.get_top_res(sess, np.zeros((3,3,3),dtype=np.uint8))
if 1:
    YOLO.inferImg(np_image=np.zeros((3,3,3),dtype=np.uint8), thresh=0.2,
                            configPath="TCDS/weights/TCDStx.cfg",
                            weightPath="TCDS/weights/TCDStx.weights",
                            metaPath="TCDS/weights/TCDStx.data")
    YOLO2.inferImg(np_image=np.zeros((3,3,3),dtype=np.uint8), thresh=0.2,
                                        configPath="TCDS/weights/TCDSsubyolo.cfg",
                                        weightPath="TCDS/weights/TCDSsubyolo.weights",
                                        metaPath="TCDS/weights/TCDSsubyolo.data")
    snapshoth=dict()
    snapshoth['t']=[4500]
    snapshoth['tf']=[4500]
    snapshoth['tb']=[4500]
    snapshoth['cf']=[11000,11800]
    snapshoth['cb']=[11000]
    snapshoth['cc']=[9500]
    camtypes=dict()
    for camname in camnames:
        if camname.startswith('t') and camname.endswith('f'): camtypes[camname] = 'tf'
        elif camname.startswith('t') and camname.endswith('b'): camtypes[camname] = 'tb'
        elif camname.startswith('c') and camname.endswith('f'): camtypes[camname] = 'cf'
        elif camname.startswith('c') and camname.endswith('b'): camtypes[camname] = 'cb'
        elif camname.startswith('c') and camname.endswith('c'): camtypes[camname] = 'cc'
        else:
            raise Exception('camtype error')
    lastheight=99999
    while True:
        tcds_statebf=mcrw.raw_read('tcds_statebf', 0)    
        tcds_statec=mcrw.raw_read('tcds_statec', 0)
        NOW = datetime.now()
        DATE = NOW.strftime('%Y-%m-%d')
        TIME = NOW.strftime('%H-%M-%S')
        plc=readplc()
        currheight=plc.getEstHoistPos()
        #print('TLOCK:',plc.TLOCK,'currheight:',currheight)
        #print('tcds_statebf,statec',tcds_statebf,tcds_statec)
        for camname in camnames:
            camtype=camtypes[camname]
            mcrw.raw_write('tcds_active', time.time())
            frame = cam[camname]
            frame_cpy = frame.copy()
            tmp = mcrw.raw_read(f'{camname}lastrawupdate', 0)

            tocontinue=0
            if tcds_statebf==0 and camname.startswith('cn') and camname[-1] in 'bf':
                tocontinue=1
            if tcds_statec==0 and camname.startswith('cn') and camname[-1] in 'c':
                tocontinue=1
            if tcds_statebf>0 and camname.startswith('t'):
                tocontinue=1
            if tcds_statebf>=4:
                tocontinue=1
            if tocontinue:
                assignimage(imshow[camname], frame_cpy)
                continue

            #if height cross snapshoth
            for _i,_snapshoth in enumerate(snapshoth[camtype]):                            
                if plc.TLOCK and plc.speed>0 and lastheight<_snapshoth and currheight>=_snapshoth:
                    if SIZE==45 and camtype=='cf':
                        _corners=''.join(map(str,cornermap[SIZE,camname,_i+1]))
                    else:
                        _corners=''.join(map(str,cornermap[SIZE,camname]))
                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/y_{camname}_corners_{_corners}_height_{int(lastheight)}_{int(currheight)}.jpg', frame)

            if SIZE==45:
                def proc1(phase=0):
                    print('proc1')
                    if phase==0:
                        assert camname.endswith('bc') or camname.endswith('bb')
                        cornermapref = cornermap[SIZE, camname]
                    else:
                        assert camname.endswith('bf')
                        cornermapref = cornermap[SIZE, camname, phase]
                    print('camname,phase,cornermapref:',camname,phase,cornermapref)

                    def proc2(x,corner):
                        print('proc2')
                        print('x',x)
                        print('corner',corner)
                        print('store',storedetection[camname].keys())
                        print('negstore',negstoredetection[camname].keys())
                        if x in storedetection[camname]:
                            _DATE, _TIME, _frame_cpy, _xc, _yc = storedetection[camname][x]
                            if mcrw.raw_read(f'tcds_corner{corner}', 0) == 0:
                                mcrw.raw_write(f'tcds_corner{corner}', time.time())
                            if not detected[camname, corner]:
                                detected[camname, corner] = True
                                printandlog(f'{JOBDATE}_{JOBTIME}', f'{_DATE}_{_TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                                cv2.putText(_frame_cpy, f'{corner}', (_xc, _yc), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)
                                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{_DATE}_{_TIME}_{camname}_{corner}.jpg', _frame_cpy)
                                sendjson('TCDS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{_DATE}_{_TIME}_{camname}_{corner}.jpg')
                        if lognegative:
                            if x in negstoredetection[camname]:
                                _DATE, _TIME, _frame_cpy, _xc, _yc = negstoredetection[camname][x]
                                if not negdetected[camname, corner]:
                                    negdetected[camname, corner] = True 
                                    cv2.putText(_frame_cpy, f'{corner}', (_xc, _yc), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)
                                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/x_{camname}_{corner}.jpg', _frame_cpy)
                    
                    lenx = []
                    for x in camscores[camname]:
                        print(f'camscores[{camname}][{x}]')
                        for s,p in camscores[camname][x]:
                            print(' ',s,p)
                        L=len(camscores[camname][x])
                        if L>=minhits:
                            lenx.append((L, x))
                    lenx = sorted(lenx)[-2:]
                    if len(lenx)==1:
                        print('= 1 bin')
                        (len0,x0)=lenx[-1]
                        corner0 = min(cornermapref)
                        for x,corner in [(x0,corner0)]:
                            proc2(x,corner)
                    elif len(lenx)==2:
                        print('> 1 bin')
                        (len0,x0),(len1,x1) = sorted(lenx, key=lambda x: x[1])
                        corner0, corner1 = cornermapref
                        for x,corner in [(x0,corner0),(x1,corner1)]:
                            proc2(x,corner)
                    else:
                        print('0 bins')                    
                if camname.startswith('cn'):
                    print('HERE 0',camname,lasttcds_statebf,tcds_statebf)
                    if lasttcds_statebf != 3 and tcds_statebf == 3:                        
                        if camname.endswith('bc') or camname.endswith('bb'):
                            print("HERE 1")
                            proc1(phase=0)
                        else:
                            assert camname.endswith('bf')
                            print("HERE 2")
                            proc1(phase=2)
                    elif camname.endswith('bf') and lasttcds_statebf != 2 and tcds_statebf == 2:
                        #resolve and reset stats for panning camera
                        #check the 2 bins with most hits
                        PAN_WAIT=time.time()
                        print("HERE 3")
                        proc1(phase=1)
                        camscores[camname] = defaultdict(list)
                        storedetection[camname] = dict()
                    else:
                        print("HERE 4")

            if PAN_WAIT>2:
                if camname.endswith('bf'):
                    if time.time()-PAN_WAIT>PAN_DELAY:
                        print("HERE 5: reset statistics")
                        PAN_WAIT=2
                        #PAN_WAIT completed reset statistics
                        camscores[camname] = defaultdict(list)
                        storedetection[camname] = dict()
                    else:
                        print("HERE 6: PAN_WAIT")
                        continue
            if tmp == camrawlastT[camname]: continue  # skip stale images
            camrawlastT[camname] = tmp
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                configPath="TCDS/weights/TCDSnp.cfg",
                                weightPath="TCDS/weights/TCDSnp.weights",
                                metaPath="TCDS/weights/TCDSnp.data")
            if len(results)>0 and plc.TLOCK:
                NOWSTR = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/extra/{camname}_height_{int(currheight):06d}_DT_{NOWSTR}.jpg', frame)
                mcrw.raw_write(f'tcds_{camtype}',time.time())
            if SIZE==45 and camtype in ['cf','cb']:
                if len(results)==1:
                    resultanchor=results[0]
                    if camtype=='cf':
                        if PAN_WAIT==0:
                            corners=cornermap[SIZE, camname, 1]
                        else:
                            corners=cornermap[SIZE, camname, 2]
                    else:
                        corners=cornermap[SIZE, camname]
                    if corners[0]<corners[1]:
                        extend='R'
                    else:
                        extend='L'
                    resultanchor = results[0]
                    #prob = result[1]
                    xc = int(resultanchor[2][0])
                    yc = int(resultanchor[2][1])
                    boxh = int(resultanchor[2][3] / 2)
                    boxw = int(resultanchor[2][2] / 2)
                    x1 = xc - boxw
                    y1 = yc - boxh
                    x2 = xc + boxw
                    y2 = yc + boxh
                    y2 = y1+4*(x2-x1)//3
                    x1orig=x1
                    y1orig=y1
                    x2orig=x2
                    y2orig=y2
                    if 'cnlsbb' in camname:
                        x1 = max(xc - 300 - 100, 0)
                        x2 = max(xc - 300 + 100, 0)
                        y1=max(y1orig,0)
                        y2=y1+4*(x2-x1)//3
                        xc=(x1+x2)/2
                        yc=(y1+y2)/2
                        results.append(['c2', 1, [xc,yc,x2-x1,y2-y1]])
                    elif extend=='L':
                        x1=max(x1orig-3*(x2orig-x1orig)//2,0)
                        x2=max(x1orig,0)
                        y1=max(y1orig,0)
                        y2=y1+4*(x2-x1)//3
                        xc=(x1+x2)/2
                        yc=(y1+y2)/2
                        results.append(['c2', 1, [xc,yc,x2-x1,y2-y1]])
                    else:
                        x1 = max(x2orig, 0)
                        x2 = max(x2orig + 3 * (x2orig - x1orig) // 2, 0)
                        y1 = max(y1orig,0)
                        y2 = y1+4*(x2-x1)//3
                        xc = (x1 + x2)/2
                        yc = (y1 + y2)/2
                        results.append(['c2', 1, [xc, yc, x2 - x1, y2 - y1]])

            for result in results:
                name = result[0]
                if type(name) == bytes:
                    name = name.decode('utf8')
                prob = result[1]
                xc = int(result[2][0])
                yc = int(result[2][1])
                boxh = int(result[2][3] / 2)
                boxw = int(result[2][2] / 2)
                x1 = max(xc - boxw,0)
                y1 = max(yc - boxh,0)
                x2 = xc + boxw
                y2 = yc + boxh
                if result[0]=='c2':
                    pass
                else:
                    y2 = y1+4*(x2-x1)//3
                frame2=frame[y1:y2,x1:x2]
                if min(frame2.shape[:2])<=10 or frame2.shape[0]/frame2.shape[1]<=1:
                    print(camname,y2,frame2.shape,'invalid frame2.shape')
                    #res=['n',1]
                    continue
                else:
                    results_ = YOLO2.inferImg(np_image=frame2, thresh=0.2,
                                        configPath="TCDS/weights/TCDSsubyolo.cfg",
                                        weightPath="TCDS/weights/TCDSsubyolo.weights",
                                        metaPath="TCDS/weights/TCDSsubyolo.data")
                    if len(results_)>0:
                        result_=max(results_,key=lambda x:x[1])
                        xc_ = int(result_[2][0])
                        yc_ = int(result_[2][1])
                        boxh_ = int(result_[2][3] / 2)
                        boxw_ = int(result_[2][2] / 2)
                        x1_ = x1+xc_ - boxw_
                        y1_ = y1+yc_ - boxh_
                        x2_ = x1+xc_ + boxw_
                        y2_ = y1+yc_ + boxh_
                        res=['p',result_[1]]
                        cv2.rectangle(frame_cpy, (x1_, y1_), (x2_, y2_), (0, 0, 255), 4)
                        cv2.putText(frame_cpy, f'{result_[1]:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 1)
                    else:
                        res=['n',1]
                    
                if res[0]=='p':
                    score=res[1]
                else:
                    score=1-res[1]

                insertscore(camscores[camname],(xc,yc),score)
                if score>0:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}:{xc}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)
                else:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}:{xc}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)

            for x in camscores[camname]:
                score,(xc,yc)=camscores[camname][x][-1]
                hit = score > 0
                hitsy=list(yc for score,(xc,yc) in camscores[camname][x] if score>0)
                numhits=len(hitsy)
                #if not hit:continue
                if SIZE!=45 or SIZE==45 and camname.startswith('t'):
                    if SIZE==45 and camname.startswith('t'):
                        mindist=9999
                        for _cornerid,_x in enumerate(cornerx[SIZE,camname]):
                            if abs(x-_x)<=mindist:
                                cornerid=_cornerid
                                mindist=abs(x-_x)
                    else:
                        cornerid=x>=1280/2
                    corner=cornermap[SIZE,camname][cornerid]
                    if hit and (max(hitsy)-min(hitsy)>hitsy_diffthresh):
                        if mcrw.raw_read(f'tcds_corner{corner}',0)==0:
                            mcrw.raw_write(f'tcds_corner{corner}', time.time())
                        if not detected[camname,corner]:
                            detected[camname, corner]=True
                            printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                            cv2.putText(frame_cpy, f'{corner}', (xc, yc), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)
                            makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{corner}.jpg',frame_cpy)
                            sendjson('TCDS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{corner}.jpg')
                    if lognegative:
                        if not negdetected[camname,corner]:
                            #printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                            negdetected[camname, corner]=True
                            cv2.putText(frame_cpy, f'{corner}', (xc, yc), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 2)
                            makedirsimwrite(f'{PHOTOLOGDIRNAME}/x{DATE}_{TIME}_{camname}_{corner}.jpg',frame_cpy)
                elif SIZE==45 and camname.startswith('cn'):
                    if hit and (camtype!='cf' and max(hitsy)-min(hitsy)>hitsy_diffthresh or camtype=='cf'):
                        if x not in storedetection[camname]:
                            storedetection[camname][x]=[DATE,TIME,frame_cpy,xc,yc]
                    if lognegative:
                        if x not in negstoredetection[camname]:
                            negstoredetection[camname][x]=[DATE,TIME,frame_cpy,xc,yc]
                else:
                    raise Exception('Should never reach here')

            assignimage(imshow[camname],frame_cpy)
        lasttcds_statebf=tcds_statebf
        lasttcds_statec=tcds_statec
        lastheight = currheight
