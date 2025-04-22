import os
def run(command):
    ret=os.system(command)
    if ret!=0:raise Exception(command)
def extractimage(vidfile,hstart,minstart,secstart,duration,Fout):
    #glob.glob(Fout.replace('%06d','*'))
    command=f'ffmpeg -y -ss {hstart}:{minstart}:{secstart} -i {vidfile} -t {duration} -c copy /tmp/1.mp4'
    run(command)
    command=f'ffmpeg -i /tmp/1.mp4 -vf fps=20  {Fout}'
    run(command)
    return sorted(glob.glob(Fout.replace('%06d','*')))
def extractimageall(vidfile,Fout,fps=10):
    DIRNAME=os.path.dirname(Fout)

    run('mkdir -p {}')
    command=f'ffmpeg -y -i {vidfile} -vf fps={fps}  {Fout}'
    run(command)
    return sorted(glob.glob(Fout.replace('%06d','*')))

def extractimage1(vidfile,start,Fout):
    command=f'ffmpeg -y -ss {start} -i {vidfile}  -vframes 1 {Fout}'
    run(command)



import time
import os
import cv2
from yolohelper import detect as YOLO
import SharedArray as sa
from tfstuff import infer
import tensorflow as tf
import glob
import re
import numpy as np
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)
imgfiles=natural_sort(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_images/*'))

tfconfig = tf.ConfigProto(
        device_count = {'GPU': 1}
    )
tfconfig.gpu_options.allow_growth = True
verbose=0
import glob
#files=glob.glob('/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-15/cnlsbb-11_25.mp4')
#files=glob.glob('/mnt/NFSDIR/RawVideos/ARMG/7409/2019-09-02/cnlsbf-20_55.mp4')
#files=glob.glob('/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-22/cnssbb-19_40.mp4')
#files=glob.glob('/mnt/NFSDIR/RawVideos/ARMG/*/2019-08-19/')
#files=['/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-19/cnlsbc-21_35.mp4']
#files=['/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-19/cnlsbb-17_05.mp4']
#files=['/mnt/NFSDIR/RawVideos/ARMG/7409/2019-08-26/cnssbb-21_45.mp4']
#files=['/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-26/cnlsbf-15_00.mp4'] #FALSEPOSITIVE
#files=['/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-26/cnlsbf-15_05.mp4']
import sys
files=[sys.argv[1]]
lastresults=[]
cv2.namedWindow("")
def doclick(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print((x,y))
cv2.setMouseCallback("", doclick)

with tf.Session(config=tfconfig, graph=infer.graph) as sess:
    infer.get_top_res(sess, np.zeros((3,3,3)))
    i=5404
    waittime=1000
    for file in files:
        cap=cv2.VideoCapture(file)
        framenum = 0
        while True:
            ret,frame=cap.read()
            framenum += 1
            if not ret:break
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                configPath="TCDS/weights/TCDSnp.cfg",
                                weightPath="TCDS/weights/TCDSnp.weights",
                                metaPath="TCDS/weights/TCDSnp.data")
            allmatch = True
            if len(results)==len(lastresults):
                for result1 in results:
                    match=False
                    xc1 = int(result1[2][0])
                    yc1 = int(result1[2][1])
                    for result2 in lastresults:
                        xc2 = int(result2[2][0])
                        yc2 = int(result2[2][1])
                        if (xc2-xc1)**2+(yc2-yc1)**2<50**2:
                            match=True
                            break
                    if not match:
                        allmatch=False
                        break
            else:
                allmatch=False
                lastresults=results
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
                y2 = y1+4*(x2-x1)//3
                frame2=frame[y1:y2,x1:x2]
                if 0 in frame2.shape:continue
                res = infer.get_top_res(sess, frame2)
                if res[0]=='p':
                    score=res[1]
                else:
                    score=1-res[1]

                if score>=0.7:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                    cv2.putText(frame, f'{xc:.0f}:{prob:.2f}:{score:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                    cv2.putText(frame, f'{xc:.0f}:{prob:.2f}:{score :.2f}:{xc:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 1)

            cv2.putText(frame, f'framenum:{framenum}', (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 1)


            lastresults=results

            cv2.imshow('',frame)
            c=cv2.waitKey(0)
            if c==ord('q'):
                raise Exception('q')
            if c==ord('1'):
                for _ in range(10):
                    ret, frame = cap.read()
                    framenum+=1
            if c==ord('2'):
                for _ in range(20):
                    ret, frame = cap.read()
                    framenum+=1
            if c==ord('3'):
                for _ in range(40):
                    ret, frame = cap.read()
                    framenum += 1
            if c==ord('4'):
                for _ in range(80):
                    ret, frame = cap.read()
                    framenum += 1
            if c==ord('5'):
                for _ in range(160):
                    ret, frame = cap.read()
                    framenum += 1
            if c==ord('6'):
                for _ in range(320):
                    ret, frame = cap.read()
                    framenum += 1
