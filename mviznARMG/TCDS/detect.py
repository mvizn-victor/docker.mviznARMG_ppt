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
with tf.Session(config=tfconfig, graph=infer.graph) as sess:
    infer.get_top_res(sess, np.zeros((3,3,3)))
    i=5404
    waittime=1000
    while True:
        frame=cv2.imread(imgfiles[i])
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
            SIZE = max(boxw, boxh) * 2
            x1 = xc - boxw
            y1 = yc - boxh
            x2 = xc + boxw
            y2 = yc + boxh
            y2 = y1+2*(x2-x1)
            frame2=frame[y1:y2,x1:x2]
            res = infer.get_top_res(sess, frame2)
            if res[0]=='p':
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                cv2.putText(frame, f'{name}:{prob:.2f}:{res[1]:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 1)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                cv2.putText(frame, f'{name}:{prob:.2f}:{res[1]:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 1)
        cv2.putText(frame, f'{i}', (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 0, 0), 1)
        if 0:
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                            configPath="TCDS/weights/TCDSp.cfg",
                            weightPath="TCDS/weights/TCDSp.weights",
                            metaPath="TCDS/weights/TCDSp.data")
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
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                cv2.putText(frame, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 1)
                cv2.putText(frame, f'{i}', (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 0, 0), 1)


        cv2.imshow('',frame)
        c=cv2.waitKey(waittime)
        if c==ord('q'):
            raise Exception('q')
        if c==ord('f'):
            waittime=1
        if c==ord('n'):
            i=i+1
            waittime = 1000
        if c==ord('p'):
            i=i-2
            waittime=1000
        i=i+1
