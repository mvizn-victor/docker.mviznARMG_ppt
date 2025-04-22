import cv2
from yolohelper import detect as YOLO
import SharedArray as sa
from tfstuff import infer
import tensorflow as tf
import glob
import re
import numpy as np
from config.config import *
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
    SIZEX=='20'

mcrw.raw_write('tcds_corner1',0)
mcrw.raw_write('tcds_corner2',0)
mcrw.raw_write('tcds_corner3',0)
mcrw.raw_write('tcds_corner4',0)



cornermap=dict()
cornermap[20,'cnlsbf']=(2,3)
cornermap[20,'cnlsbb']=(4,1)
cornermap[20,'cnlsbc']=(4,4)
cornermap[20,'tl20f']=(3,3)
cornermap[20,'tl20b']=(4,4)
cornermap[20,'cnssbf']=(2,3)
cornermap[20,'cnssbb']=(4,1)
cornermap[20,'cnssbc']=(1,1)
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

cornermap[45,'cnlsbf',1]=(2,2)
cornermap[45,'cnlsbf',2]=(3,3)
cornermap[45,'cnlsbb']=(1,1)
cornermap[45,'cnlsbc']=(4,4)
cornermap[45,'tl4xf']=(3,3)
cornermap[45,'tl4xb']=(4,4)
cornermap[45,'cnssbf',1]=(3,3)
cornermap[45,'cnssbf',2]=(2,2)
cornermap[45,'cnssbb']=(4,4)
cornermap[45,'cnssbc']=(1,1)
cornermap[45,'ts4xf']=(2,2)
cornermap[45,'ts4xb']=(1,1)

camnames=[f'cn{SIDE}sbf',f'cn{SIDE}sbb',f'cn{SIDE}sbc',f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b']
#camnames=[f'cn{SIDE}sbf',f'cn{SIDE}sbb',f'cn{SIDE}sbc']
cam=dict()
camrawlastT=dict()
camscores=dict()
from collections import deque
detected=dict()

numbins=1280//64
for camname in camnames:
    cam[camname]=sa.attach(f'shm://{camname}_raw')
    camrawlastT[camname]=0
    for bin in range(numbins):
        camscores[camname,bin]=[]
    for corner in range(1,5):
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
            if tcds_statebf==0 and camname.startswith('cn') and camname[-1] in 'bf':
                continue
            if tcds_statec==0 and camname.startswith('cn') and camname[-1] in 'c':
                continue
            if camname[-1]=='f' and lasttcds_statebf != 2 and tcds_statebf == 2:
                #reset stats for panning camera
                for bin in range(numbins):
                    camscores[camname, bin] = []
            if tcds_statebf>0 and camname.startswith('t'):
                continue
            if tcds_statebf==3:
                continue
            frame = cam[camname]
            frame_cpy = frame.copy()
            tmp = mcrw.raw_read(f'{camname}lastrawupdate', 0)
            if tmp == camrawlastT[camname]: continue  # skip stale images
            camrawlastT[camname] = tmp
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
                y2 = y1+4*(x2-x1)//3
                frame2=frame[y1:y2,x1:x2]
                res = infer.get_top_res(sess, frame2)
                bin=xc//64
                if res[0]=='p':
                    score=res[1]
                else:
                    score=1-res[1]
                camscores[camname,bin].append(score)
                if score>=0.7:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)
                else:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame_cpy, f'{prob:.2f}:{score:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)

            for bin in range(numbins):
                right=bin>=numbins/2
                if SIZE==45 and camname.endswith=='bf':
                    if tcds_statebf==2:
                        corner = cornermap[SIZE, camname, 2][right]
                    else:
                        corner = cornermap[SIZE, camname, 1][right]
                else:
                    corner = cornermap[SIZE, camname][right]
                if len(camscores[camname, bin])>=3:
                    if all(x>=0.7 for x in camscores[camname,bin][-3:]):
                        if mcrw.raw_read(f'tcds_corner{corner}',0)==0:
                            mcrw.raw_write(f'tcds_corner{corner}', time.time())
                        if not detected[camname,corner]:
                            detected[camname, corner]=True                            
                            printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, corner, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                            makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{corner}.jpg',frame_cpy)
            assignimage(imshow[camname],frame_cpy)
        lasttcds_statebf=tcds_statebf
