from config.config import *
import time
import os
import numpy as np
import cv2
import sys
ps=[]
def doclick(event, x, y, flags, param):
    global ex_left,ex_right
    if event == cv2.EVENT_LBUTTONDOWN:
        #print((x*8//3, y*8//3),(x,y))
        print((x,y))
        ps.append((x,y))
        if len(ps)>=2:
            x1,y1=ps[-2]
            x2,y2=ps[-1]
            line=np.poly1d(np.polyfit([x1,x2],[y1,y2],1))
            ex_left=int(line(0))
            ex_right=int(line(w))
            print(ex_left,ex_right)
            os.makedirs('config/hncds',exist_ok=True)
            fout=f'config/hncds/{camname}.txt'
            print(0,ex_left,0,0,w,0,w,ex_right,file=open(fout,'w'))
            print(f'written to {fout}')
    if event == cv2.EVENT_RBUTTONDOWN:
        sys.exit(0)                    
cv2.namedWindow("")            
cv2.setMouseCallback("", doclick)
camname=sys.argv[1]
cam=eval(camname)
def updateimage():
    global frame0
    #cam.snapshot('/tmp/1.jpg')
    #time.sleep(1)
    jpeg=cam.snapshotimage()
    open('/tmp/1.jpg','wb').write(jpeg)
    frame0=cv2.imread('/tmp/1.jpg')
updateimage()
h,w=frame0.shape[:2]
while True:
    frame=frame0.copy()
    if len(ps)>=2:
        cv2.line(frame, (0,ex_left),(w,ex_right),(0,255,0), 3)
    cv2.imshow("", frame)
    k=cv2.waitKey(1)
    if k==ord('q'):
        sys.exit(0)
    if k==ord('n'):
        updateimage()
    #line=np.poly1d(np.polyfit([bottomy,topy],[bottomx1,topx1],1))

