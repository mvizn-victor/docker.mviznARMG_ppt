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
img=sys.argv[1]
frame0=cv2.imread(img)
h,w=frame0.shape[:2]
while True:
    frame=frame0.copy()
    cv2.imshow("", frame)
    k=cv2.waitKey(1)        
    if k==ord('q'):
        sys.exit(0)

