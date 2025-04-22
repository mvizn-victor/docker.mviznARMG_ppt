import cv2

from yolohelper import detect as YOLO
from yolohelper import detect2 as YOLO2
from yolohelper import detect3 as YOLO3

import SharedArray as sa
ovls=sa.attach('shm://ovls_raw')
#while True:
#    frame=ovls.copy()
import glob
#files=glob.glob('/home/mvizn/Desktop/tmp/*.mp4')
#files=['/mnt/NFSDIR/RawVideos/ARMG/7409/2019-09-02/ts20b-16_10.mp4']
files=['/home/mvizn/Code/htmlvideo/static/videos/HNCDSside/a1/997347_7110_2019-09-17_ts20f-22_00.mp4']
files=['/mnt/NFSDIR/RawVideos/ARMG/7110/2019-09-11/cnlsbc-15_05.mp4']
files=['/mnt/NFSDIR/YardVideos_converted/20190701/CNLSBF/7110_CNLSBF_20190531_190000.mp4']
#files=['/home/mvizn/Code/htmlvideo/static/videos/HNCDSside/a1/75774_7409_2019-09-09_ts20b-14_20.mp4']
for file in files*100:
    cap=cv2.VideoCapture(file)
    framenum = 0
    while True:
        ret,frame=cap.read()
        framenum+=1
        if not ret:break
        results = YOLO.inferImg(np_image=frame, thresh=0.1,
                            configPath="HNCDS/weights/HNCDSside.cfg",
                            weightPath="HNCDS/weights/HNCDSside.weights",
                            metaPath="HNCDS/weights/HNCDSside.data")
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            if name not in ['p','tp']:continue
            name='p'
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
            cv2.rectangle(frame, (x1, y1)
                          , (x2, y2), (255, 0, 0), 4)
            cv2.putText(frame, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 1)

        cv2.putText(frame, f'framenum:{framenum}', (15, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 0, 0), 1)
        cv2.imshow('',frame)
        c=cv2.waitKey(9990)
        if c==ord('q'):
            raise
        if c==ord('s'):
            break
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