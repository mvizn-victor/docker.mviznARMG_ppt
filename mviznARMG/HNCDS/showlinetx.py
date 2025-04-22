from config.config import *
import time
import os
import numpy as np
import cv2
import sys
w,h,x0,y0=1920,1080,100,50
camnames=['tl20f','tl20b','tl4xf','tl4xb','ts20f','ts20b','ts4xf','ts4xb']
n=len(camnames)
import math
cols = int(math.ceil(n ** 0.5))
rows = int(math.ceil(n / cols))
w1=(w-x0)//cols
h1=(h-y0*(rows+1))//rows
for i,camname in enumerate(camnames):
    row=i//cols
    col=i%cols
    cv2.namedWindow(camname)
    cv2.moveWindow(camname, x0+col * w1, y0+row*(h1+y0))


frames=dict()
polygons=dict()
cv2.namedWindow(camname)
for camname in camnames:
    polygons[camname]=[]
    try:
        x1,y1,x2,y2,x3,y3,x4,y4=map(int,open(f'/home/mvizn/Code/mviznARMG/config/hncds/{camname}.txt').read().strip().split())
        polygon=[(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
        polygons[camname].append(polygon)
    except:
        pass
    cam=eval(camname)
    cam.snapshot('/tmp/1.jpg')
    time.sleep(1)
    frames[camname]=cv2.imread('/tmp/1.jpg')
    for polygon in polygons[camname]:
        cv2.line(frames[camname], (polygon[0][0],polygon[0][1]),(polygon[-1][0],polygon[-1][1]),(0,255,0), 3)
    cv2.imshow(camname,scaleimage(frames[camname],w1,h1))   
cv2.waitKey(0)     
