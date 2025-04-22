import cv2
from yolohelper import detect as YOLO


import SharedArray as sa
#ovls=sa.attach('shm://ovls_raw')
#while True:
#    frame=ovls.copy()
import glob
#files=glob.glob('/home/mvizn/Desktop/tmp/*.mp4')
import sys
from Utils.helper import procimage
if len(sys.argv)<2:
    files=['HNCDS/sample/2.mp4']
else:
    files=[sys.argv[1]]
    if len(sys.argv)>=3:
        outfile=sys.argv[2]
    else:
        outfile='/tmp/out.mp4'
for f in files*1:
    cap=cv2.VideoCapture(f)    
    framenum = 0
    while True:
        ret,frame=cap.read()
        framenum+=1
        #if framenum<90*25:continue
        if not ret:break
        results=procimage('hncdssideyolo',frame)
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
            if name=='p' and procimage('hncdsinception',frame[max(y1,0):y2,max(x1,0):x2])[0]!='p':
                continue
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
            cv2.putText(frame, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 1)
            cv2.imshow('',frame)
            cv2.waitKey(0)
        cv2.imshow('',frame)

        c=cv2.waitKey(1)
        if c==ord('q'):
            raise('q')
        if c==ord('s'):
            break
