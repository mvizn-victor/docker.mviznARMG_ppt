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
    if event == cv2.EVENT_MBUTTONDOWN:
        if len(ps)>=2:
            os.makedirs('config/hncds',exist_ok=True)
            fout=f'config/hncds/{camname}.txt'
            print(0,ex_left,0,0,w,0,w,ex_right,file=open(fout,'w'))
            print(f'written to {fout}')
    if event == cv2.EVENT_RBUTTONDOWN:
        sys.exit(0)                    
cv2.namedWindow("")            
cv2.setMouseCallback("", doclick)
vid=sys.argv[1]
camname=sys.argv[2]
cap=cv2.VideoCapture(vid)
ret,frame0=cap.read()
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
        ret,frame0=cap.read()
    #line=np.poly1d(np.polyfit([bottomy,topy],[bottomx1,topx1],1))

