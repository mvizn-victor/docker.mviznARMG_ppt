#cluster down arrows

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
                    newmask[0:np.max(np.argwhere(mask[:,i]==1))+0,i]=1
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

from scipy.spatial.distance import cdist, pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
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
def calcmags(prev,next):
    prev = cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY)
    next = cv2.cvtColor(next,cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev,next, None, 0.5, 3, 30, 3, 5, 1.2, 0)
    mags=np.zeros(flow.shape[:2])
    mags[:,:]=np.sqrt(flow[:,:,0]**2+flow[:,:,1]**2)
    return mags

from collections import deque
import time
prefix=sys.argv[1]
import glob
fs=sorted(glob.glob(f'{prefix}*.jpg'))
assert len(fs)>0
origcamname=os.path.basename(prefix)
outdir=os.path.dirname(prefix).replace('/raw',f'/flowtest14/{origcamname}')
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
if 1:
    for f,t in zip(fs,ts):
        T0=time.time()
        image[camname] = cv2.imread(f)
        image_cpy[camname] = image[camname].copy()
        duration=(t-lastt)/100
        #distcutoff=min(duration/0.5*30,100)
        distcutoff=100
        #distcutoff=200
        newmask[camname]=maskoutcontainer(image[camname], False)
        print(camname,1,time.time()-T0)
        mind=9999
        maxd=0
        mindx=9999
        maxdx=0
        largestdownclustersize=0
        if lastimage[camname] is not None:
            out, kpxy, lastsift[camname] = bsmatcher(lastimage[camname], image[camname], lastnewmask[camname], newmask[camname], sift0=lastsift[camname])
            print(camname,2,time.time()-T0)
            mags=calcmags(lastimage[camname],image[camname])            
            #out = list((tuple(x[0]), tuple(x[1])) for x in out if dist(x[1], x[0]) <= distcutoff or (mags[int(x[0][1]),int(x[0][0])]>=10 and dist(x[1], x[0]) <= distcutoff2))
            def printret(s,x):
                print(s,x)
                return x
            #out = list((tuple(x[0]), tuple(x[1])) for x in out if dist(x[1], x[0]) <= distcutoff or (printret('a',dist(x[1], x[0]))<=printret('b',mags[int(x[1][1]),int(x[1][0])]*3)))
            out = list((tuple(x[0]), tuple(x[1])) for x in out if dist(x[1], x[0]) <= distcutoff)
            #out = list of vectors from lastimage to currentimage which are within 100 pixels
            linktoorigin[camname] = dict()
            #linktoorigin[camname] and lastlinktoorigin[camname] are dictionary of sourcepoint->(originpoint,age)
            tmp1 = list(lastlinktoorigin[camname].keys())
            for x in out:
                tmp1b = withindist(x[0], tmp1, 10)
                if len(tmp1b) > 0:
                    #link source point to oldest feature tie break with nearer distance
                    tmp2 = max(list((lastlinktoorigin[camname][tuple(p)], d) for p, d in tmp1b), key=lambda x: (x[0][1], -x[1]))[0]
                    #print("HERE1:",tmp2)
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
            dxs=defaultdict(list)
            for k2, (k1, age) in linktoorigin[camname].items():
                x1.append(k1[0])
                y1.append(k1[1])
                x2.append(k2[0])
                y2.append(k2[1])
                ds[(x1[-1],y1[-1])].append(y2[-1] - y1[-1])
                dxs[(x1[-1], y1[-1])].append(x2[-1] - x1[-1])                
            dup=dict()
            ddown=dict()
            dright=dict()
            dleft=dict()
            validdownstarts=[]
            for k in ds:
                dup[k]=min(ds[k])
                ddown[k]=max(ds[k])
                dright[k]=max(dxs[k])
                dleft[k]=min(dxs[k])
                if ddown[k]>=maxthresh[camtype]:
                    validdownstarts.append(k)
            from collections import Counter
            if len(validdownstarts)>0:
                graph=squareform(pdist(validdownstarts))<=100
                graph = csr_matrix(graph)
                clusters=connected_components(graph)[1]
                largestdownclustersize=max(Counter(clusters).values())
            else:
                largestdownclustersize=0
            
            _3largest=heapq.nlargest(3,ddown.values())
            _3smallest=heapq.nsmallest(3,dup.values())
            _3largestx = heapq.nlargest(3, dright.values())
            _3smallestx = heapq.nsmallest(3, dleft.values())
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
            if len(_3smallestx) >= 3:
                mindx = _3smallestx[2]
            if len(_3largestx) >= 3:
                maxdx = _3largestx[2]
            for _x1, _y1, _x2, _y2 in zip(x1, y1, x2, y2):
                if _y2-_y1<=minthresh[camtype]:
                    color=(0,0,255)
                elif _y2-_y1>=maxthresh[camtype]:
                    color=(0,255,0)
                    cv2.circle(image_cpy[camname],(_x1,_y1),100,color,1)
                else:
                    color=(255,0,0)
                cv2.arrowedLine(image_cpy[camname],(_x1,_y1),(_x2,_y2),color,2)
            lastlinktoorigin[camname] = linktoorigin[camname]
            print(camname,3,time.time()-T0)        
        lastnewmask[camname] = newmask[camname]
        lastimage[camname] = image[camname]
        image_cpy[camname] = overlaymask(newmask[camname],image_cpy[camname])
        cv2.imwrite(f'{outdir}/{camname}_{t:06d}.jpg',image_cpy[camname])
        #assignimage(imshow[camname],image_cpy[camname])
        lastt=t
        #if mind<=minthresh[camtype] or maxd>=maxthresh[camtype]:
        if mind<=minthresh[camtype] or largestdownclustersize>=3:
            triggered=1
            cv2.imwrite(f'{outdir}_triggered.jpg',image_cpy[camname])
            print('triggered')
            #break
if not triggered:
    cv2.imwrite(f'{outdir}_nottriggered.jpg',image_cpy[camname])
    print('not triggered')
