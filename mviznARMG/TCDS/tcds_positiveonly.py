import cv2
from yolohelper import detect as YOLO
import SharedArray as sa
from tfstuff import infer
import tensorflow as tf
import glob
import re
import numpy as np
from config.config import *
from config.cornerx import cornerx
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

os.environ['CUDA_VISIBLE_DEVICES']='1'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'
tfconfig = tf.ConfigProto(
        device_count = {'GPU': 1}
    )

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

cornermap=dict()
cornermap[20,'cnlsbf']=(2,3)
cornermap[20,'cnlsbb']=(4,1)
cornermap[20,'cnlsbc']=(4,4)
cornermap[20,'tl20f']=(3,3)
cornermap[20,'tl20b']=(4,4)
cornermap[20,'cnssbf']=(2,3)
cornermap[20,'cnssbb']=(4,1)
cornermap[20,'cnssbc']=(2,2)
cornermap[20,'ts20f']=(2,2)
cornermap[20,'ts20b']=(1,1)


cornermap[40,'cnlsbf']=(2,3)
cornermap[40,'cnlsbb']=(1,1)
cornermap[40,'cnlsbc']=(4,4)
cornermap[40,'tl4xf']=(3,3)
cornermap[40,'tl4xb']=(4,4)
cornermap[40,'cnssbf']=(2,3)
cornermap[40,'cnssbb']=(4,1)
cornermap[40,'cnssbc']=(1,1)
cornermap[40,'ts4xf']=(2,2)
cornermap[40,'ts4xb']=(1,1)

cornermap[45,'cnlsbf',1]=(2,6)
cornermap[45,'cnlsbf',2]=(7,3)
cornermap[45,'cnlsbb']=(5,1)
cornermap[45,'cnlsbc']=(8,4)
cornermap[45,'tl4xf']=(3,7)
cornermap[45,'tl4xb']=(8,4)
cornermap[45,'cnssbf',1]=(7,3)
cornermap[45,'cnssbf',2]=(2,6)
cornermap[45,'cnssbb']=(4,8)
cornermap[45,'cnssbc']=(5,1)
cornermap[45,'ts4xf']=(6,2)
cornermap[45,'ts4xb']=(1,5)

camnames=[f'cn{SIDE}sbf',f'cn{SIDE}sbb',f'cn{SIDE}sbc',f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b']
#camnames=[f'cn{SIDE}sbf',f'cn{SIDE}sbb',f'cn{SIDE}sbc']
cam=dict()
camrawlastT=dict()
camscores=dict()
from collections import deque,defaultdict
detected=dict()
storedetection=dict()
def insertscore(bindict,x,score):
    inserted=False
    for k in bindict:
        if abs(x-k)<=bindist:
            bindict[k].append((score,x))
            inserted=True
            break
    if not inserted:
        bindict[x].append((score,x))

bindist=50
for camname in camnames:
    cam[camname]=sa.attach(f'shm://{camname}_raw')
    camrawlastT[camname]=0
    camscores[camname]=defaultdict(list)
    storedetection[camname]=dict()
    for corner in range(1,9):
        detected[camname,corner]=False

os.system('rm /dev/shm/*_tcds')
imshow=dict()
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_tcds')

Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/TCDS/photologs/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/TCDS/logs/{JOBDATE}.txt'

lasttcds_statebf=0
with tf.Session(config=tfconfig, graph=infer.graph) as sess:
    infer.get_top_res(sess, np.zeros((3,3,3),dtype=np.uint8))
    YOLO.inferImg(np_image=np.zeros((3,3,3),dtype=np.uint8), thresh=0.2,
                            configPath="TCDS/weights/TCDSnp.cfg",
                            weightPath="TCDS/weights/TCDSnp.weights",
                            metaPath="TCDS/weights/TCDSnp.data")
    while True:
        tcds_statebf=mcrw.raw_read('tcds_statebf', 0)
        tcds_statec=mcrw.raw_read('tcds_statec', 0)
        NOW = datetime.now()
        DATE = NOW.strftime('%Y-%m-%d')
        TIME = NOW.strftime('%H-%M-%S')

        for camname in camnames:
            mcrw.raw_write('tcds_active', time.time())
            frame = cam[camname]
            frame_cpy = frame.copy()
            tmp = mcrw.raw_read(f'{camname}lastrawupdate', 0)
            if tmp == camrawlastT[camname]: continue  # skip stale images
            camrawlastT[camname] = tmp
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

            if SIZE==45:
                def proc1(phase=0):
                    if phase==0:
                        assert camname.endswith('bc')
                        cornermapref = cornermap[SIZE, camname]
                    else:
                        cornermapref = cornermap[SIZE, camname, phase]
                    if len(camscores[camname]) == 1:
                        # assume is outer corner
                        corner = min(cornermapref)
                        for x in camscores[camname]:
                            if x in storedetection[camname]:
                                _DATE, _TIME, _frame_cpy = storedetection[camname][x]
                                if mcrw.raw_read(f'tcds_corner{corner}', 0) == 0:
                                    mcrw.raw_write(f'tcds_corner{corner}', time.time())
                                if not detected[camname, corner]:
                                    detected[camname, corner] = True
                                    printandlog(f'{JOBDATE}_{JOBTIME}', f'{_DATE}_{_TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/{_DATE}_{_TIME}_{camname}_{corner}.jpg', _frame_cpy)
                    elif len(len(s) >= 3 for s in camscores[camname]) >= 2:
                        # more than two bins with more than 3 hits
                        lenx = []
                        for x in camscores[camname]:
                            lenx.append((len(camscores[camname][x]), x))
                        lenx = sorted(lenx)[-2:]
                        x0, x1 = sorted(lenx, key=lambda x: x[1])
                        corner0, corner1 = cornermapref
                        for x,corner in [(x0,corner0),(x1,corner1)]:
                            if x in storedetection[camname]:
                                _DATE, _TIME, _frame_cpy = storedetection[camname][x]
                                if mcrw.raw_read(f'tcds_corner{corner}', 0) == 0:
                                    mcrw.raw_write(f'tcds_corner{corner}', time.time())
                                if not detected[camname, corner]:
                                    detected[camname, corner] = True
                                    printandlog(f'{JOBDATE}_{JOBTIME}', f'{_DATE}_{_TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/{_DATE}_{_TIME}_{camname}_{corner}.jpg', _frame_cpy)
                if camname.startswith('cn'):
                    if lasttcds_statebf != 3 and tcds_statebf == 3:
                        if camname.endswith('bc'):
                            proc1(phase=0)
                        else:
                            proc1(phase=2)
                    elif camname.endswith('bf') and lasttcds_statebf != 2 and tcds_statebf == 2:
                        #resolve and reset stats for panning camera
                        #check the 2 bins with most hits
                        proc1(phase=1)
                        camscores[camname] = dict()
                        storedetection[camname] = dict()


            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                configPath="TCDS/weights/TCDSnp.cfg",
                                weightPath="TCDS/weights/TCDSnp.weights",
                                metaPath="TCDS/weights/TCDSnp.data")

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
                y2 = y1+5*(x2-x1)//3
                frame2=frame[y1:y2,x1:x2]
                if min(frame2.shape[:2])<=10 or frame2.shape[0]/frame2.shape[1]<=0.5:
                    print(camname,y2,frame2.shape,'invalid frame2.shape')
                    res=['n',1]
                else:
                    res = infer.get_top_res(sess, frame2)

                if res[0]=='p':
                    score=res[1]
                else:
                    score=1-res[1]
                insertscore(camscores[camname],xc,score)
                if score>=0.7:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}:{xc}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)
                else:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}:{xc}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)

            for x in camscores[camname]:
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
                    if len(camscores[camname][x])>=3:
                        if all(s[0]>=0.7 for s in camscores[camname][x][-3:]):
                            if mcrw.raw_read(f'tcds_corner{corner}',0)==0:
                                mcrw.raw_write(f'tcds_corner{corner}', time.time())
                            if not detected[camname,corner]:
                                detected[camname, corner]=True
                                printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{corner}.jpg',frame_cpy)
                elif SIZE==45 and camname.startswith('cn'):
                    if len(camscores[camname][x])>=3:
                        if all(s[0]>=0.7 for s in camscores[camname][x][-3:]):
                            if x not in storedetection[camname]:
                                storedetection[camname][x]=[DATE,TIME,frame_cpy]
                else:
                    raise Exception('Should never reach here')

            assignimage(imshow[camname],frame_cpy)
        lasttcds_statebf=tcds_statebf
        lasttcds_statec=tcds_statec
