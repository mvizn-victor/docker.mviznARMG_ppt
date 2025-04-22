#version:1
from datetime import datetime,timedelta
import time
from memcachehelper import memcacheRW as mcrw
import cv2
import os
from yolohelper import detect as YOLO


import SharedArray as sa
camraw=dict()
for camname in ['ovls','ovss','pmnls','pmnss']:
    camraw[camname]=sa.attach(f"shm://{camname}_raw")
for (i,camname) in enumerate(['ovls','pmnls','ovss','pmnss']):
    cv2.namedWindow(camname)
    cv2.moveWindow(camname,(i%2)*600,(i//2)*500)
frames=dict()
#every 10seconds
lastT1=0
while True:
    mcrw.raw_write('hncds_lastT',time.time())
    T1=time.time()//1
    #reset every 1 second

    datetimeT1=datetime.fromtimestamp(T1)
    DATE=datetimeT1.strftime('%Y-%m-%d')
    TIME=datetimeT1.strftime('%H-%M-%S')
    lastT1=T1
    va=0
    vh=0
    vp=0
    for camname in ['ovls','ovss','pmnls','pmnss']: 
        frame=camraw[camname]
        frame_cpy=frame.copy()
        frames[camname]=frame_cpy
        results = YOLO.inferImg(np_image=frame, thresh=0.2,
                            configPath="HNCDS/weights/HNCDS.cfg",
                            weightPath="HNCDS/weights/HNCDS.weights",
                            metaPath="HNCDS/weights/HNCDS.data")
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            if name=='a' or name=='c':
                va=1       
                mcrw.raw_write('last_hncds_a',time.time())
            elif name=='h':
                vh=1
                mcrw.raw_write('last_hncds_h',time.time())
            elif name=='p':
                vp=1
                mcrw.raw_write('last_hncds_p',time.time())                         
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
            if name=='a' or name=='c':color=(255,0,0)
            if name=='h':color=(0,255,0)
            if name=='p':color=(0,0,255)
            cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), color, 4)
            cv2.putText(frame_cpy, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (255, 0, 0), 2)
        if len(results)>0:
            violations=vp*'p'+va*'a'+vh*'h'
            os.makedirs(f'/opt/captures/HNCDS/photologs/{DATE}',exist_ok=True)
            cv2.imwrite(f'/opt/captures/HNCDS/photologs/{DATE}/{TIME}_{camname}_{violations}.jpg',frame_cpy)
            os.makedirs('/opt/captures/HNCDS/logs',exist_ok=True)
            print(f'{DATE}_{TIME}',camname,violations,sep=",")
            print(f'{DATE}_{TIME}',camname,violations,file=open(f'/opt/captures/HNCDS/logs/{DATE}.txt','a'),sep=",")
            
    
    for camname in ['ovls','ovss','pmnls','pmnss']:        
        cv2.imshow(camname, cv2.resize(frames[camname],(480,270)))
        #cv2.imshow(camname, cv2.resize(frames[camname],(1280,720)))
    c=cv2.waitKey(1)
    if c==ord('q'):
        raise
        
