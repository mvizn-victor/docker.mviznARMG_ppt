import cv2

from yolohelper import detect as YOLO


import SharedArray as sa
ovls=sa.attach('shm://ovls_raw')
#while True:
#    frame=ovls.copy()
import glob
#files=glob.glob('/home/mvizn/Desktop/tmp/*.mp4')
files=['/mnt/NFSDIR/YardVideos_converted/20190701/OVTRSS/7110_OVTRSS_20190617_010000.mp4']

for file in files*100:
    cap=cv2.VideoCapture(file)
    framenum = 0
    while True:
        ret,frame=cap.read()
        framenum+=1
        if framenum<13*25*60*2:continue
        if not ret:break

        results = YOLO.inferImg(np_image=frame, thresh=0.2,
                            configPath="HNCDS/weights/HNCDS.cfg",
                            weightPath="HNCDS/weights/HNCDS.weights",
                            metaPath="HNCDS/weights/HNCDS.data")
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
        cv2.imshow('',frame)
        c=cv2.waitKey(1)
        if c==ord('q'):
            raise
        if c==ord('s'):
            break