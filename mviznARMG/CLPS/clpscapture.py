saveimages=1

from config.config import *
from datetime import datetime,timedelta
import os
os.environ['CUDA_VISIBLE_DEVICES']='1'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'

import sys
sys.path.append('Mask_RCNN')
import numpy as np
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from mrcnn import visualize
import matplotlib
# Agg backend runs without a display
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import cv2
plt.rcParams['figure.figsize'] = [20, 10]
model_path='CLPS/weights/clps.h5'


class VocConfig(Config):
    NAME = "voc"

    IMAGE_PER_GPU = 2

    NUM_CLASSES = 1 + 20  # VOC 2012 have 20 classes. "1" is for background.

    STEPS_PER_EPOCH = 100


class InferenceConfig(VocConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    DETECTION_MIN_CONFIDENCE = 0


VOC_CLASSES = ['_background_', 'c']
VocConfig.NUM_CLASSES = len(VOC_CLASSES)
InferenceConfig.NUM_CLASSES = len(VOC_CLASSES)
config = InferenceConfig()


def maskoutcontainer(image0,maskout=True):
    r0 = model.detect([image0], verbose=0)[0]
    if 0:visualize.display_instances(
                    image0, r0['rois'], r0['masks'], r0['class_ids'],
                    VOC_CLASSES, r0['scores'],
                    show_bbox=True, show_mask=True,
                    title="Predictions")
    newmask=np.zeros(image0.shape[:2],dtype=bool)
    for maski in range(len(r0['class_ids'])):
        mask=r0['masks'][:,:,maski]
        for i in range(mask.shape[1]):
            try:
                newmask[0:np.max(np.argwhere(mask[:,i]==1)),i]=1
            except:
                pass
    #newmask[:,0:np.min(np.argwhere(newmask),axis=0)[1]]=1
    #newmask[:,np.max(np.argwhere(newmask),axis=0)[1]:]=1
    newmask[:,np.max(newmask,axis=0)==False]=1
    if maskout:
        image0[newmask]=0
    return newmask

def bsmatcher(image0,image1,newmask0,newmask1,draw=False,sift0=None):
    import numpy as np
    import cv2 as cv
    import matplotlib.pyplot as plt
    #img1 = cv.imread('box.png',cv.IMREAD_GRAYSCALE)          # queryImage
    #img2 = cv.imread('box_in_scene.png',cv.IMREAD_GRAYSCALE) # trainImage
    img1=image0
    img2=image1
    # Initiate SIFT detector
    sift = cv.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    if sift0 is not None:
        kp1, des1 = sift0
    else:
        kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)   # or pass empty dictionary
    flann = cv.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]
    # ratio test as per Lowe's paper
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.7*n.distance:
            x1,y1=cv2.KeyPoint_convert(kp1)[m.queryIdx]
            x1,y1=int(x1),int(y1)
            x2,y2=cv2.KeyPoint_convert(kp2)[m.trainIdx]
            x2,y2=int(x2),int(y2)
            if not newmask0[y1,x1] and not newmask1[y2,x2]:
                matchesMask[i]=[1,0]
    draw_params = dict(matchColor = (0,255,0),
                       singlePointColor = (255,0,0),
                       matchesMask = matchesMask,
                       flags = cv.DrawMatchesFlags_DEFAULT)
    if draw:
        img3 = cv.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)
        plt.imshow(img3)
    out=[]
    for match in list(matches[i][0] for i in np.argwhere(np.array(matchesMask))[:,0]):
        #print(cv2.KeyPoint_convert(kp1)[match.queryIdx],cv2.KeyPoint_convert(kp2)[match.trainIdx])
        #out.append(abs(cv2.KeyPoint_convert(kp1)[match.queryIdx][1]-cv2.KeyPoint_convert(kp2)[match.trainIdx][1]))
        out.append([cv2.KeyPoint_convert(kp1)[match.queryIdx],cv2.KeyPoint_convert(kp2)[match.trainIdx]])
    return out,cv2.KeyPoint_convert(kp2),(kp2,des2)

from scipy.spatial.distance import cdist
def dist(x,y):
    return ((x[0]-y[0])**2+(x[1]-y[1])**2)**.5
def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]

def mindist(node, nodes):
    try:
        d=cdist([node], nodes)
        mind=d.min()
        argmind=d.argmin()
    except:
        mind=9999
        argmind=None
    return mind,argmind
def withindist(node,nodes,threshold):
    if len(nodes)==0:
        return []
    else:
        d=cdist([node], nodes)[0]
        return list( (_node,_d) for _node,_d in zip(nodes,d) if _d<=threshold)


from collections import deque
import time
plc=readplc()
SIDE=plc.SIDE
SIZE=plc.size
if SIZE>=40:SIZEX='4x'
else:SIZEX='20'
camnames=[f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b',f'cn{SIDE}sbf',f'cn{SIDE}sbb']
cam=dict()
for camname in camnames:
    cam[camname]=sa.attach(f'shm://{camname}_raw')

#wait for twistlock
#wait for plc.LAND to get first frame
lastimage=dict()
linktoorigin = dict()
lastlinktoorigin = dict()
image=dict()
newmask=dict()
lastnewmask=dict()
lastsift=dict()
images=dict()
for camname in camnames:
    lastimage[camname] = None
    linktoorigin[camname] = dict()
    lastlinktoorigin[camname] = dict()
    image[camname] = None
    lastsift[camname] = None
    from collections import deque
    images[camname]=deque([])
###COMMON###
imshow=dict()
os.system('rm /dev/shm/*_clps')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_clps')

Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/CLPS/photologs/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/CLPS/logs/{JOBDATE}.txt'

liftdetected=0
mcrw.raw_write('clps_liftdetected',0)
liftstart=0
lastland=0

#model=modellib.MaskRCNN(mode='inference',config=config,model_dir='')
#model.load_weights(model_path, by_name=True)
#model.detect([np.zeros((3,3,3))], verbose=0)[0]

import pickle
while True:
    mcrw.raw_write('clps_active',time.time())
    T=time.time()
    plc=readplc()
    pickle.dump(plc,makedirsopen(f'CLPScapture/{JOBDATE}_{JOBTIME}/{int(T*10)}.dat','wb'))
    for camname in camnames:
        assignimage(imshow[camname],cam[camname])
        makedirsimwrite(f'CLPScapture/{JOBDATE}_{JOBTIME}/{int(T*10)}_{camname}.jpg',cam[camname])
    Telapsed=time.time()-T
    time.sleep(max(0.5-Telapsed,0))
