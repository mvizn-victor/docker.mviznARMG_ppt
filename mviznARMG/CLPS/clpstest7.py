
from multiprocessing import Pool
#maskrcnn using docker tfserve
import sys
sys.path.append('mrcnn_serving_ready')
from inferencing.saved_model_inference import detect_mask_single_image

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
if 0:
    plt.rcParams['figure.figsize'] = [20, 10]
    model_path='CLPS/weights/resnet101_sideonly.h5'
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
    r0 = detect_mask_single_image(image0)
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
    for maski in range(len(r0['class'])):
        mask=r0['mask'][:,:,maski]
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
    if 1:
        sift = cv.xfeatures2d.SIFT_create()
    else:
        sift = cv2.ORB()
    # find the keypoints and descriptors with SIFT
    if sift0 is not None:
        kp1, des1 = sift0
    else:
        #kp1, des1 = sift.detectAndCompute(img1, None)
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
deploy=0
video=sys.argv[1]
outvideo=sys.argv[2]
outdir=os.path.dirname(outvideo)
outprefix=os.path.basename(outvideo)
#wait for twistlock
#wait for plc.LAND to get first frame

###COMMON###

if deploy:
    Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
else:
    Tjobstart=datetime.now()

if deploy:
    JOBDATE=Tjobstart.strftime("%Y-%m-%d")
    JOBTIME=Tjobstart.strftime("%H-%M-%S")
    PHOTOLOGDIRNAME=f'/opt/captures/CLPS/photologs/{JOBDATE}/{JOBTIME}'
    LOGFILENAME=f'/opt/captures/CLPS/logs/{JOBDATE}.txt'
else:
    JOBDATE=Tjobstart.strftime("%Y-%m-%d")
    JOBTIME=Tjobstart.strftime("%H-%M-%S")
    PHOTOLOGDIRNAME=f'/opt/capturestest/CLPS/photologs/{JOBDATE}/{JOBTIME}'
    LOGFILENAME=f'/opt/capturestest/CLPS/logs/{JOBDATE}.txt'


liftdetected=0
mcrw.raw_write('clps_liftdetected',0)
liftstart=0
lastland=0
if 0:
    model=modellib.MaskRCNN(mode='inference',config=config,model_dir='')
    model.load_weights(model_path, by_name=True)
    model.detect([np.zeros((3,3,3))], verbose=0)[0]
minthresh = dict(txxx=-80, cnxx=-30)
maxthresh = dict(txxx=25, cnxx=9999)

def clpscam(video):
    for camname in ['ts4xf','ts4xb','ts20f','ts20b','tl4xf','tl4xb','tl20f','tl20b']:
        if camname in video:
            break
    lastimage = dict()
    linktoorigin = dict()
    lastlinktoorigin = dict()
    image = dict()
    image_cpy = dict()
    images = dict()
    newmask = dict()
    lastnewmask = dict()
    lastsift = dict()
    ds = dict()
    dup = dict()
    ddown = dict()
    if 1:
        lastimage[camname] = None
        linktoorigin[camname] = dict()
        lastlinktoorigin[camname] = dict()
        image[camname] = None
        lastsift[camname] = None
        images[camname] = deque([])
    cami=0
    T = time.time()
    cap = cv2.VideoCapture(video)
    framenum = -1
    while True:
        ret,frame=cap.read()
        framenum += 1
        if not ret:
            break
        if framenum==0:
            vidh,vidw=frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"MP4V")
            vidout = cv2.VideoWriter(outvideo, fourcc, 1, (vidw,vidh))
        if framenum%5!=0:continue
        if framenum>20*5:break
        print(camname,cami)
        if camname.startswith('t'): camtype = 'txxx'
        if camname.startswith('cn'): camtype = 'cnxx'
        if 1:
            image[camname]=frame
            image_cpy[camname] = frame.copy()
        T0=time.time()
        newmask[camname]=maskoutcontainer(image[camname], False)
        print(camname,1,time.time()-T0)
        mind=9999
        maxd=0
        if lastimage[camname] is not None:
            out, kpxy, lastsift[camname] = bsmatcher(lastimage[camname], image[camname], lastnewmask[camname], newmask[camname], sift0=lastsift[camname])
            print(camname,2,time.time()-T0)
            out = list((tuple(x[0]), tuple(x[1])) for x in out if dist(x[1], x[0]) < 100)
            #out = list of vectors from lastimage to currentimage which are within 100 pixels
            linktoorigin[camname] = dict()
            #linktoorigin[camname] and lastlinktoorigin[camname] are dictionary of sourcepoint->(originpoint,age)
            tmp1 = list(lastlinktoorigin[camname].keys())
            for x in out:
                tmp1b = withindist(x[0], tmp1, 10)
                if len(tmp1b) > 0:
                    #link source point to oldest feature tie break with nearer distance
                    tmp2 = max(list((lastlinktoorigin[camname][tuple(p)], d) for p, d in tmp1b), key=lambda x: (x[0][1], -x[1]))[0]
                    print("HERE1:",tmp2)
                else:
                    #lastlink defaults to current point whose age is 0
                    tmp2 = (x[0], 0)
                #update if no entry yet or there is an older link
                #direct current point(x[1]) to oldest origin(tmp2[0])
                if x[1] not in linktoorigin[camname] or linktoorigin[camname][x[1]][1] <= tmp2[1] + 1:
                    linktoorigin[camname][x[1]] = (tmp2[0], tmp2[1] + 1)

            from collections import defaultdict
            import heapq
            x1=[]
            y1=[]
            x2=[]
            y2=[]
            ds=defaultdict(list)
            for k2, (k1, age) in linktoorigin[camname].items():
                x1.append(k1[0])
                y1.append(k1[1])
                x2.append(k2[0])
                y2.append(k2[1])
                ds[(x1[-1],y1[-1])].append(y2[-1] - y1[-1])
            dup=dict()
            ddown=dict()
            for k in ds:
                dup[k]=min(ds[k])
                ddown[k]=max(ds[k])
            _3largest=heapq.nlargest(3,ddown.values())
            _3smallest=heapq.nsmallest(3,dup.values())
            for i in range(3):
                font = cv2.FONT_HERSHEY_SIMPLEX
                if i<len(_3smallest):
                    cv2.putText(image_cpy[camname], '%.2f'%_3smallest[i], (0, 100 + i * 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                if 2-i<len(_3largest):
                    cv2.putText(image_cpy[camname], '%.2f' % _3largest[2-i], (0, 400 + i * 100), font, 1, (0, 255,0), 2, cv2.LINE_AA)
            if len(_3smallest) >= 3:
                mind = _3smallest[2]
            if len(_3largest) >= 3:
                maxd = _3largest[2]
            for _x1, _y1, _x2, _y2 in zip(x1, y1, x2, y2):
                if _y2-_y1<=minthresh[camtype]:
                    color=(0,0,255)
                elif _y2-_y1>=maxthresh[camtype]:
                    color=(0,255,0)
                else:
                    color=(255,0,0)
                cv2.arrowedLine(image_cpy[camname],(_x1,_y1),(_x2,_y2),color,2)
            lastlinktoorigin[camname] = linktoorigin[camname]
            print(camname,3,time.time()-T0)
        lastnewmask[camname] = newmask[camname]
        lastimage[camname] = image[camname]
        image_cpy[camname] = overlaymask(newmask[camname],image_cpy[camname])
        cv2.imshow('out',image_cpy[camname])
        vidout.write(image_cpy[camname])
        if camtype == 'txxx' and (maxd >= maxthresh[camtype] or mind <= minthresh[camtype]):
            if not os.path.exists(f'{outdir}/{outprefix}.jpg'):
                cv2.imwrite(f'{outdir}/{outprefix}.jpg', image_cpy[camname])
        cv2.waitKey(1)

        T=time.time()

        cami=cami+1
    vidout.release()
    if not os.path.exists(f'{outdir}/{outprefix}.jpg'):
        cv2.imwrite(f'{outdir}/{outprefix}.jpg', image_cpy[camname])
    #time.sleep(3)

if __name__ == '__main__':

    if 1:
        os.system('bash mrcnnserve_local.sh')
        pass
    #camnames=[camnames[0]]
    clpscam(video)
    #readFrametoShm(videoinput[5])
    #print("Workers launched")

