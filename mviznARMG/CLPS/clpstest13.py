#2
#optical flow
import heapq
from armgws.armgws import sendjson
from multiprocessing import Pool
#maskrcnn using docker tfserve
import sys
#sys.path.append('mrcnn_serving_ready')
#from inferencing.saved_model_inference import detect_mask_single_image

saveimages=0

from config.config import *
from datetime import datetime,timedelta
import os
os.environ['CUDA_VISIBLE_DEVICES']='1'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'

import sys
sys.path.append('Mask_RCNN')
import numpy as np
#from mrcnn.config import Config
#from mrcnn import model as modellib, utils
#from mrcnn import visualize
import matplotlib
# Agg backend runs without a display
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import cv2
import time
Tstart=time.time()
def overlaymask(mask,image,alpha=0.5):
    overlay = image.copy()
    output = image.copy()
 
    # draw a red rectangle surrounding Adrian in the image
    # along with the text "PyImageSearch" at the top-left
    # corner
    overlay[mask]=(255,0,0)    
    cv2.addWeighted(overlay, alpha, output, 1 - alpha,0, output)
    return output
       
def maskoutcontainer(image0,maskout=True):
    from Utils.helper import procimage
    r0 = procimage('clpsmaskrcnn',image0)
    if 0:visualize.display_instances(
                    image0, r0['rois'], r0['masks'], r0['class_ids'],
                    VOC_CLASSES, r0['scores'],
                    show_bbox=True, show_mask=True,
                    title="Predictions")
    elif 0:
        visualize.display_instances(
            image0, r0['rois'], r0['mask'], r0['class'],
            VOC_CLASSES, r0['scores'],
            show_bbox=True, show_mask=True,
            title="Predictions")
    newmask=np.zeros(image0.shape[:2],dtype=bool)
    classids=r0['class_ids']
    for maski in range(len(r0['class_ids'])):
        if classids[maski]==1:
            mask=r0['masks'][:,:,maski]
            for i in range(mask.shape[1]):
                try:
                    newmask[0:np.max(np.argwhere(mask[:,i]==1))+40,i]=1
                except:
                    pass
    #newmask[:,0:np.min(np.argwhere(newmask),axis=0)[1]]=1
    #newmask[:,np.max(np.argwhere(newmask),axis=0)[1]:]=1
    newmask[:,np.max(newmask,axis=0)==False]=1
    for maski in range(len(r0['class_ids'])):
        if classids[maski]!=1:
            mask=r0['masks'][:,:,maski]
            newmask[mask]=1    
    if maskout:
        image0[newmask]=0
    return newmask

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis=img
    #vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (_x2, _y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis
def flatten(x,step=8):
    h,w=x.shape[:2]
    #y,x=np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    y,x=np.mgrid[:h, :w].reshape(2,-1)
    fx,fy=flow[y,x].T
    return h,w,y,x,fx,fy
def unflatten(h,w,y,x,fx,fy):
    flow=np.zeros((h,w,2))
    flow[y,x]=np.array([fx,fy]).T
    return flow


from collections import deque
import time
prefix=sys.argv[1]
#prefix='/mnt/NFSDIR/ARMG-Project-Data/captures/7106/captures/CLPS/photologs/2020-09-02/14-31-17/raw/ts20b'
import glob
fs=sorted(glob.glob(f'{prefix}*.jpg'))
assert len(fs)>0
origcamname=os.path.basename(prefix)
outdir=os.path.dirname(prefix).replace('/raw',f'/flowtest13/{origcamname}')
#outdir=sys.argv[2]
os.makedirs(outdir,exist_ok=True)
os.system(f'rm {outdir}/*')
ts=[0]
for f in fs[:-1]:
    _,t=os.path.basename(f)[:-4].split('_')
    ts.append(int(t))
print(ts)    
       
#wait for twistlock
#wait for plc.LAND to get first frame
lastimage=dict()
linktoorigin = dict()
lastlinktoorigin = dict()
image=dict()
image_cpy=dict()
images=dict()
newmask=dict()
lastnewmask=dict()
lastsift=dict()
ds=dict()
dup=dict()
ddown=dict()
if 1:
    camtype='txxx'
    camname='test'
    lastimage[camname] = None
    linktoorigin[camname] = dict()
    lastlinktoorigin[camname] = dict()
    image[camname] = None
    lastsift[camname] = None
    images[camname]=deque([])
minthresh = dict(txxx=-80, cnxx=-30)
maxthresh = dict(txxx=25, cnxx=9999)
minthreshx = dict(txxx=-80, cnxx=-9999)
maxthreshx = dict(txxx=80, cnxx=9999)
lastt=0
triggered=0
cumflow=np.zeros((720, 1280, 2),dtype=np.float32)
if 1:
    for f,t in zip(fs,ts):
        T0=time.time()
        image[camname] = cv2.imread(f)
        next = cv2.cvtColor(image[camname],cv2.COLOR_BGR2GRAY)
        if lastimage[camname] is not None:
            prev = cv2.cvtColor(lastimage[camname],cv2.COLOR_BGR2GRAY)
        else:
            prev = next
        flow = cv2.calcOpticalFlowFarneback(prev,next, None, 0.5, 3, 30, 3, 5, 1.2, 0)
        image_cpy[camname] = image[camname].copy()
        newmask[camname]=maskoutcontainer(image[camname], False)
        print(camname,1,time.time()-T0)
        h,w,y,x,fx,fy=flatten(flow)
        prevy=np.clip(((y-fy)).astype(int),0,h-1)
        prevx=np.clip(((x-fx)).astype(int),0,w-1)
        prevfx,prevfy=cumflow[prevy,prevx].T
        cumflow=unflatten(h,w,y,x,prevfx+fx,prevfy+fy)
        cumflow[newmask[camname]]=[0,0]
        _50largest=heapq.nlargest(50,cumflow[...,1].flatten())
        _50smallest=heapq.nsmallest(50,cumflow[...,1].flatten())        
        _3largest=[_50largest[0],_50largest[10],_50largest[20]]
        _3smallest=[_50smallest[0],_50smallest[10],_50smallest[20]]
        for i in range(3):
            font = cv2.FONT_HERSHEY_SIMPLEX
            if i<len(_3smallest):
                cv2.putText(image_cpy[camname], '%.2f'%_3smallest[i], (0, 100 + i * 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if 2-i<len(_3largest):
                cv2.putText(image_cpy[camname], '%.2f' % _3largest[2-i], (0, 400 + i * 100), font, 1, (0, 255,0), 2, cv2.LINE_AA)            
        lastnewmask[camname] = newmask[camname]
        lastimage[camname] = image[camname]
        image_cpy[camname] = overlaymask(newmask[camname],image_cpy[camname])
        draw_flow(image_cpy[camname],-cumflow,16)
        cv2.imwrite(f'{outdir}/{camname}_{t:06d}.jpg',image_cpy[camname])                
        #assignimage(imshow[camname],image_cpy[camname])
        lastt=t
        #if mind<=minthresh[camtype] or maxd>=maxthresh[camtype]:
        if 0 and (mind<=minthresh[camtype] or largestdownclustersize>=3):
            triggered=1
            cv2.imwrite(f'{outdir}_triggered.jpg',image_cpy[camname])
            print('triggered')
            break
if 0:
    if not triggered:
        cv2.imwrite(f'{outdir}_nottriggered.jpg',image_cpy[camname])
        print('not triggered')
