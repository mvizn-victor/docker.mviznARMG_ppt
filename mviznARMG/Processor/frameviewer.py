import cv2
from config.config import *
import SharedArray as sa

cams={}
camids=[]
for x in videoinput:
    camid=x[0]
    if 'ovtr' not in camid:
        camids.append(camid)
        cams[camid]=sa.attach(f'shm://{camid}_raw')
while True:
    for camid in camids:
        cv2.imshow(camid,cams[camid])
        cv2.waitKey(1)