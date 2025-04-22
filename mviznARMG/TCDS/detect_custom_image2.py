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
    run('mkdir -p {DIRNAME}')
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
#imgfiles=natural_sort(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_images/*'))

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
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_l_1/f*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_l_1/b*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_l_1/c*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_l_2/f*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_l_3/f*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_s_1/f*.jpg'))
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_s_2/f*.jpg')) #2687 fp, 2814 fp
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/day_45_s_3/f*.jpg')) #2256 fp
#files=sorted(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/night_45_l_1/f*.jpg')) #1860 fp


lastresults=[]
fout=open('/tmp/res_20191124.txt','w')
with tf.Session(config=tfconfig, graph=infer.graph) as sess:
    infer.get_top_res(sess, np.zeros((3,3,3)))
    for daynight in ['day','night']:
        for size in ['45','40','20']:
            for side in ['l','s']:
                for i in [1,2,3]:
                    for cam in ['f', 'b', 'c', 'tf', 'tb']:
                        fileprefix=f'/mnt/NFSDIR/ARMG-Project-Data/TCDS_samplevideos/{daynight}_{size}_{side}_{i}/{cam}'
          12              print(fileprefix)
                        files = sorted(glob.glob(f'{fileprefix}*.jpg'))
                        framenum=0
                        while True:
                            #framenum=framenum%len(files)
                            if framenum>=len(files):break
                            frame=cv2.imread(files[framenum])
                            results = YOLO.inferImg(np_image=frame, thresh=0.1,
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
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                                    cv2.putText(frame, f'{prob:.2f}:{res[1]:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 0, 0), 1)
                                else:
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                                    cv2.putText(frame, f'{prob:.2f}:{res[1]:.2f}', (x1, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                                (255, 0, 0), 1)
                                if res[0]=='p':score=prob
                                else:score=1-prob
                                print(fileprefix, framenum, xc, yc, score, file = fout)
                            cv2.putText(frame, f'framenum:{framenum}', (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (255, 0, 0), 1)
                            if len(results)>0:
                                imout=fileprefix.replace('TCDS_samplevideos','TCDS_samplevideos_res')
                                os.makedirs(os.path.dirname(imout),exist_ok=True)
                                cv2.imwrite(f'{imout}_{framenum}.jpg',frame)
                            cv2.imshow('',frame)
                            c=cv2.waitKey(1)
                            if c==ord('q'):
                                raise Exception('q')
                            if c==ord('6'):
                                framenum+=1
                            elif c==ord('7'):
                                framenum+=10
                            elif c==ord('8'):
                                framenum+=20
                            elif c==ord('9'):
                                framenum +=40
                            elif c==ord('0'):
                                framenum+=80
                            elif c==ord('5'):
                                framenum-=1
                            elif c==ord('4'):
                                framenum-=10
                            elif c==ord('3'):
                                framenum-=20
                            elif c==ord('2'):
                                framenum-=40
                            elif c==ord('1'):
                                framenum-=80
                            framenum += 1