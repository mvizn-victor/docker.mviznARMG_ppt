#version:1
#cluster down arrows
from yolohelper import detect as YOLO
from armgws.armgws import sendjson
from multiprocessing import Pool
import sys
saveimages=0

from config.config import *
from datetime import datetime,timedelta
import os
import sys
sys.path.append('Mask_RCNN')
import numpy as np
from scipy import stats
#from mrcnn.config import Config
#from mrcnn import model as modellib, utils
#from mrcnn import visualize
# Agg backend runs without a display
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import cv2
import time
configPath='CDODS/weights/CDODS.cfg'
weightPath='CDODS/weights/CDODS.weights'
metaPath='CDODS/weights/CDODS.data'
thresh=0.2
vid=sys.argv[1]
cap=cv2.VideoCapture(vid)
framenum=0
maxang=0
while True:
    ret, frame = cap.read()
    h, w = frame.shape[:2]
    if not ret:break
    framenum += 1
    if framenum==1:
        vidh,vidw=frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*"MP4V")
        vidout = cv2.VideoWriter('/tmp/out.mp4', fourcc, 10, (vidw,vidh))
        
    results = YOLO.inferImg(np_image=frame, thresh=thresh,
                            configPath=configPath,
                            weightPath=weightPath,
                           metaPath=metaPath)
    xs=[]
    ys=[]
    xys=[]    
    for i,result in enumerate(results):
        name = result[0]
        if type(name)==bytes:
            name = name.decode('utf8')               
        prob = result[1]
        if name!='p':
            if prob<0.2:continue            
        xc = int(result[2][0])
        yc = int(result[2][1])
        boxh = int(result[2][3] / 2)
        boxw = int(result[2][2] / 2)
        x1 = max(xc - boxw, 0)
        y1 = max(yc - boxh, 0)
        x2 = xc + boxw
        y2 = yc + boxh
        # p=red t=green b=yellow s=blue
        #colors = dict(p=(0, 0, 255), t=(0, 255, 0), b=(0, 255, 255), s=(255, 255, 0))
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 1)
        font = cv2.FONT_HERSHEY_SIMPLEX 
          
        # org 
        org = (x1, y1) 
          
        # fontScale 
        fontScale = 1
           
        # Blue color in BGR 
        color = (255, 0, 0) 
                      
        # Line thickness of 2 px 
        thickness = 1
           
        # Using cv2.putText() method 
        image = cv2.putText(frame, f'{name}:{prob:.2f}', org, font,  
                           fontScale, color, thickness, cv2.LINE_AA)
        xs.append(xc)
        ys.append(yc)
        xys.append((xc,yc))
    if 0:
        if len(xs)>0:
            slope, intercept, r_value, p_value, std_err = stats.linregress(xs, ys)
            cv2.putText(frame, ("std_err: %.3g" % (std_err)), (20,40), font,  
                               fontScale, (0,0,255), 2, cv2.LINE_AA)
    if len(xs)==4:
        xys.sort()
        x1,x2,x3,x4=list(xy[0] for xy in xys)
        y1,y2,y3,y4=list(xy[1] for xy in xys)
        line1=np.poly1d(np.polyfit([x1,x2],[y1,y2],1))
        line2=np.poly1d(np.polyfit([x3,x4],[y3,y4],1))
        line1left=int(x1-(x2-x1)/2)
        line1right=int(x2+(x2-x1)/2)
        line2left=int(x3-(x4-x3)/2)
        line2right=int(x4+(x4-x3)/2)
        ex_left1=int(line1(line1left))
        ex_right1=int(line1(line1right))
        ex_left2=int(line2(line2left))
        ex_right2=int(line2(line2right))
        cv2.line(frame, (line1left,ex_left1),(line1right,ex_right1),(0,255,0), 1)
        cv2.line(frame, (line2left,ex_left2),(line2right,ex_right2),(0,255,0), 1)        
        #cv2.line(frame, (0,ex_left1),(w,ex_right1),(0,255,0), 1)
        #cv2.line(frame, (0,ex_left2),(w,ex_right2),(0,255,0), 1)
        #_, ang1 = cv2.cartToPolar(np.float32([x2-x1]),np.float32([y2-y1]))
        #_, ang2 = cv2.cartToPolar(np.float32([x4-x3]),np.float32([y4-y3]))
        #ang1=(ang1[0][0]*180/np.pi)%180
        #ang2=(ang2[0][0]*180/np.pi)%180
        def magnitude(x,y):
            return (x*x+y*y)**.5
        dotprod=((x2-x1)*(x4-x3)+(y2-y1)*(y4-y3))/(magnitude(x2-x1,y2-y1)*magnitude(x4-x3,y4-y3))
        ang=np.arccos(dotprod)*180/np.pi
        if ang>maxang:
            maxang=ang
        cv2.putText(frame, f'ang:{ang:5.1f} maxang:{maxang:5.1f}', (20,40), font,  
                               fontScale, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow('out',frame)
    vidout.write(frame)
    k=cv2.waitKey(1)
    if k==ord('q'):
        sys.exit(0)
        
