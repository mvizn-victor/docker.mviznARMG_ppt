#version:fcj
#eak:
#erode3dilate51,mog2 for both source and dest,movementarrow>2,stationaryarrow<=2,movementarrow 
#need to be accompanied by mog2 motion, stationary arrow keep alive last arrow otherwise causes 
#arrow spreading,bruteforcematcher instead of flannmatcher, ratio test 0.7 to 0.8, down arrow filter not(y2-y1>20 and dist(p1,p2)>50);
#ejk:
#ignore top 1/3 of image for down and moveoff. up will still take into account top 1/3
#moveoff logic
#-points with arrow parallel within 15 degree and parallel component exceed 25 px are validpar points
#ejv:
#lift logic ignore "moveoff arrow"
#fcj:
#extend mask downwards 10px to reduce container arrow
def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

from armgws.armgws import sendjson
from multiprocessing import Pool
#maskrcnn using docker tfserve
import sys
#sys.path.append('mrcnn_serving_ready')
#from inferencing.saved_model_inference import detect_mask_single_image

saveimages=1

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
                    newmask[0:np.max(np.argwhere(mask[:,i]==1))+10,i]=1
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
        try:
            sift = cv.xfeatures2d.SIFT_create()
        except:
            sift = cv.SIFT_create()
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
    if 0:
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)   # or pass empty dictionary
        flann = cv.FlannBasedMatcher(index_params,search_params)
        matches = flann.knnMatch(des1,des2,k=2)
    if 1:
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1,des2, k=2)        
    
    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]
    # ratio test as per Lowe's paper
    T=time.time()
    ckp1=cv2.KeyPoint_convert(kp1)
    ckp2=cv2.KeyPoint_convert(kp2)
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.8*n.distance:
            x1,y1=ckp1[m.queryIdx]
            x1,y1=int(x1),int(y1)
            x2,y2=ckp2[m.trainIdx]
            x2,y2=int(x2),int(y2)
            if not newmask0[y1,x1] and not newmask1[y2,x2]:
                matchesMask[i]=[1,0]
    draw_params = dict(matchColor = (0,255,0),
                       singlePointColor = (255,0,0),
                       matchesMask = matchesMask,
                       flags = cv.DrawMatchesFlags_DEFAULT)
    print(time.time()-T)
    if draw:
        img3 = cv.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,**draw_params)
        plt.imshow(img3)
    out=[]
    for match in list(matches[i][0] for i in np.argwhere(np.array(matchesMask))[:,0]):
        #print(cv2.KeyPoint_convert(kp1)[match.queryIdx],cv2.KeyPoint_convert(kp2)[match.trainIdx])
        #out.append(abs(cv2.KeyPoint_convert(kp1)[match.queryIdx][1]-cv2.KeyPoint_convert(kp2)[match.trainIdx][1]))
        out.append([ckp1[match.queryIdx],ckp2[match.trainIdx]])
    return out,ckp2,(kp2,des2)

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


from collections import deque
import time
deploy=1
configfolder='config'
if len(sys.argv)>1:
    deploy=0
    imgsrcfolder=sys.argv[1]
    crane=imgsrcfolder.strip('/').split('/')[-7]
    configfolder=f'/home/mvizn/Code/jupyter/ARMG/config_{crane}'
    if not os.path.exists(configfolder):
        configfolder=f'/home/mvizn/Code/mviznARMG/config'

    try:
        imgoutfolder=sys.argv[2]
        os.system(f'rm -rf "{imgoutfolder}"')
    except:
        imgoutfolder=None

if deploy:
    plc=readplc()
    SIDE=plc.SIDE
    SIZE=plc.size
    if SIZE>=40:SIZEX='4x'
    else:SIZEX='20'
    camnames=[f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b']
    #camnames=[f't{SIDE}{SIZEX}f',f't{SIDE}{SIZEX}b',f'cn{SIDE}sbf',f'cn{SIDE}sbb']
    cam = dict()
    for camname in camnames:
        cam[camname] = sa.attach(f'shm://{camname}_raw')
else:
    #photologsdir='/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/CLPS/photologs'
    imgfiles0=sorted(glob.glob(f'{imgsrcfolder}/*.jpg'))
    imgfiles=dict()
    Timg=dict()
    for imgfile in imgfiles0:
        x=imgfile.split('/')
        camname = x[-1].split('_')[0]
        SIDE=camname[1]
        if camname not in imgfiles:
            imgfiles[camname]=[]
            Timg[camname]=[]
        imgfiles[camname].append(imgfile)
        Timg[camname].append(imgfile.split('_')[-1].split('.')[0])
    camnames=sorted(imgfiles.keys())
    #print(imgfiles)
def dotprod(v1,v2):
    dx1,dy1=v1
    dx2,dy2=v2
    return dx1*dx2+dy1*dy2
def crossprod(v1,v2):
    dx1,dy1=v1
    dx2,dy2=v2
    return dx1*dy2-dy1*dx2
def getangle(v1,uv):
    #-ve if v1 clockwise of u
    sinx=np.clip((crossprod(v1,uv)+1e-6)/(np.linalg.norm(v1)+1e-6),-1,1)
    return np.arcsin(sinx)/np.pi*180
unitvector=dict()
polygon=dict()
for camname in camnames:
    unitvector[camname]=[1,0]
    f=f'{configfolder}/hncds/{camname}.txt'
    if os.path.exists(f):
        x1,y1,w1,w2,w3,w4,x2,y2=open(f).read().strip().split()
        x1,y1,x2,y2=map(int,[x1,y1,x2,y2])
        dy=y2-y1
        dx=x2-x1
        L=(dx*dx+dy*dy)**.5
        unitvector[camname]=[dx/L,dy/L]
        polygon[camname]=np.array([x1,y1,w1,w2,w3,w4,x2,y2],dtype=np.int32).reshape((-1,1,2))

#wait for twistlock
#wait for plc.LAND to get first frame
lastimage=dict()
linktoorigin = dict()
lastlinktoorigin = dict()
image=dict()
image_cpy=dict()
image_cpy2=dict()
images=dict()
newmask=dict()
lastnewmask=dict()
lastsift=dict()
ds=dict()
dup=dict()
ddown=dict()
fgbg=dict()
fgmask=dict()
kernelbig = np.ones((51,51),np.uint8)
kernel9 = np.ones((9,9),np.uint8)
kernel7 = np.ones((7,7),np.uint8)
kernel5 = np.ones((5,5),np.uint8)
kernel3 = np.ones((3,3),np.uint8)
for camname in camnames:
    lastimage[camname] = None
    linktoorigin[camname] = dict()
    lastlinktoorigin[camname] = dict()
    image[camname] = None
    lastsift[camname] = None
    images[camname]=deque([])
###COMMON###
imshow=dict()
os.system('rm /dev/shm/*_clps')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_clps')

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
    if imgoutfolder is not None:
        PHOTOLOGDIRNAME=imgoutfolder
        LOGFILENAME=f'/dev/null'
    else:
        PHOTOLOGDIRNAME=f'/opt/capturestest/CLPS/photologs/{JOBDATE}/{JOBTIME}'
        LOGFILENAME=f'/opt/capturestest/CLPS/logs/{JOBDATE}.txt'


mcrw.raw_write('clps_liftdetected',0)
for camname in ['ts20b','ts20f','tl20b','tl20f','ts4xb','ts4xf','tl4xb','tl4xf']:
    mcrw.raw_write(f'clps_moveoffdetected_{camname}', 0)
if 0:
    model=modellib.MaskRCNN(mode='inference',config=config,model_dir='')
    model.load_weights(model_path, by_name=True)
    model.detect([np.zeros((3,3,3))], verbose=0)[0]
minthresh = dict(txxx=-90, cnxx=-30)
maxthresh = dict(txxx=25, cnxx=9999)
if SIDE=='l':
    minthresh_dpar = dict(txxx=-25, cnxx=-9999)
    maxthresh_dpar = dict(txxx=9999, cnxx=9999)
elif SIDE=='s':
    minthresh_dpar = dict(txxx=-9999, cnxx=-9999)
    maxthresh_dpar = dict(txxx=25, cnxx=9999)

lastt=0
triggered=0
def clpscam(camname):
    fgbg[camname] = cv2.createBackgroundSubtractorMOG2()
    liftstart=0
    liftdetected=0
    lastland=0
    cami=0
    T = time.time()
    #init
    #maskoutcontainer(cam[camname], False)
    if deploy:
        while True:
            mcrw.raw_write('clps_active',time.time())
            plc=readplc()
            if plc.TLOCK and lastland and not plc.LAND:
                liftstart=time.time()
                LIFTSTARTDATETIME = datetime.fromtimestamp(liftstart)
                LIFTSTARTDATE = LIFTSTARTDATETIME.strftime('%Y-%m-%d')
                LIFTSTARTTIME = LIFTSTARTDATETIME.strftime('%H-%M-%S.%f')
                if camname == camnames[0]:
                    printandlog(f'{JOBDATE}_{JOBTIME}','LIFTSTART',f'{LIFTSTARTDATE}_{LIFTSTARTTIME}', file = makedirsopen(LOGFILENAME, 'a'), sep = ",")
                    printandlog('',file=makedirsopen(f'{PHOTOLOGDIRNAME}/{LIFTSTARTDATE}_{LIFTSTARTTIME}_liftstart.txt','w'))
            if liftstart:break
            if camname == camnames[0]:print('WAITING FOR TLOCK and (LAND go OFF)')
            assignimage(imshow[camname],cam[camname])
            time.sleep(0.1)
            lastland=plc.LAND
    t=time.time()
    cum_moveoff=0
    cum_liftup=0
    cum_liftdown=0    
    while True:
        mcrw.raw_write('clps_active',time.time())
        NOW=datetime.now()
        DATE = NOW.strftime('%Y-%m-%d')
        if deploy:        
            TIME = NOW.strftime('%H-%M-%S')
        else:
            TIME = NOW.strftime('%H-%M-%S')
            TIME += "."+str(int(NOW.microsecond/1e5))
        print(camname,cami)
        if camname.startswith('t'): camtype = 'txxx'
        if camname.startswith('cn'): camtype = 'cnxx'
        
        if deploy:
            plc=readplc()
            if plc.TLOCK and plc.getEstHoistPos()>6000 or time.time()-liftstart>30 or plc.speed<0:
                break
            image[camname]=cam[camname].copy()
            image_cpy[camname] = image[camname].copy()
            image_cpy2[camname] = image[camname].copy()
            #ignore frame if image connection lost
            if not image[camname].any():
                continue
            lastt=t
            t=time.time()
        else:
            loop=False
            if cami >= len(imgfiles[camname]):
                if loop:
                    cami=0
                else:
                    break
            print('cami',cami,len(imgfiles[camname]))
            lastt=t
            t=time.time()
            image[camname]=cv2.imread(imgfiles[camname][cami])
            image_cpy[camname] = image[camname].copy()
            image_cpy2[camname] = image[camname].copy()
        H,W=image[camname].shape[:2]

        T0=time.time()
        duration=(t-lastt)
        #distcutoff=min(duration/0.5*30,100)
        distcutoff=100
        distcutoffdown1=50
        distcutoffdown2=20
        distcutoff_stationarydist=2
        distcutoff_withindist=10
        newmask[camname]=maskoutcontainer(image[camname], False)
        fgmask[camname] = np.uint8(fgbg[camname].apply(image[camname])>=127)*255
        fgmask[camname] = cv2.erode(fgmask[camname],kernel3,iterations = 1)
        fgmask[camname] = cv2.dilate(fgmask[camname],kernelbig,iterations = 1)
        print(camname,1,time.time()-T0)
        mind=9999
        maxd=0
        mindx=9999
        maxdx=0
        validpar=set()
        parset=set()
        largestdownclustersize=0
        moveoff=0
        liftup=0
        liftdown=0
        if lastimage[camname] is not None:
            out, kpxy, lastsift[camname] = bsmatcher(lastimage[camname], image[camname], lastnewmask[camname], newmask[camname], sift0=lastsift[camname])
            print(camname,2,time.time()-T0)
            out = list((tuple(x[0]), tuple(x[1])) for x in out if 
                (dist(x[1], x[0]) <= distcutoff and not (dist(x[1], x[0]) > distcutoffdown1 and x[1][1]-x[0][1]>distcutoffdown2)) and
                fgmask[camname][int(x[1][1]),int(x[1][0])]>0 and fgmask[camname][int(x[0][1]),int(x[0][0])]>0 or dist(x[1],x[0])<=distcutoff_stationarydist)
            #out = list of vectors from lastimage to currentimage which are within 100 pixels
            linktoorigin[camname] = dict()
            #linktoorigin[camname] and lastlinktoorigin[camname] are dictionary of sourcepoint->(originpoint,age)
            tmp1 = list(lastlinktoorigin[camname].keys())
            for x in out:
                #cv2.arrowedLine(image_cpy2[camname],(x[0][0],x[0][1]),(x[1][0],x[1][1]),(255,255,0),2)
                tmp1b = withindist(x[0], tmp1, distcutoff_withindist)
                if len(tmp1b) > 0:
                    #link source point to oldest feature tie break with nearer distance
                    tmp2a = max(list((lastlinktoorigin[camname][tuple(p)], d,tuple(p)) for p, d in tmp1b), key=lambda x: (x[0][1], -x[1]))
                    tmp2=tmp2a[0]
                    if dist(x[0],x[1])<=distcutoff_stationarydist:
                        k=tmp2a[2]
                    else:
                        k=x[1]
                    #print("HERE1:",tmp2)                    
                else:
                    #lastlink defaults to current point whose age is 0
                    tmp2 = (x[0], 0)
                    k=x[1]
                #update if no entry yet or there is an older link
                #direct current point(x[1]) to oldest origin(tmp2[0])
                if k not in linktoorigin[camname]:
                    linktoorigin[camname][k] = (tmp2[0], tmp2[1] + 1)
                else:
                    if linktoorigin[camname][k][1] <= tmp2[1] + 1:
                        linktoorigin[camname][k] = (tmp2[0], tmp2[1] + 1)

            from collections import defaultdict
            import heapq
            x1=[]
            y1=[]
            x2=[]
            y2=[]
            yx1=[]
            yy1=[]
            yx2=[]
            yy2=[]
            #y partial line without arrowhead
            ds=defaultdict(list)
            for k2, (k1, age) in linktoorigin[camname].items():
                x1.append(k1[0])
                y1.append(k1[1])
                x2.append(k2[0])
                y2.append(k2[1])
                dpar=dotprod([x2[-1] - x1[-1],y2[-1] - y1[-1]],unitvector[camname])
                angle=getangle([x2[-1] - x1[-1],y2[-1] - y1[-1]],unitvector[camname])        
                ignore_for_updown=0
                if y1[-1]>=H/3:
                    parset.add((x1[-1],y1[-1]))
                    if abs(angle)<=15 and not (minthresh_dpar[camtype]<=dpar<=maxthresh_dpar[camtype]):
                        if abs(minthresh_dpar[camtype])!=9999:
                            dcutoff=minthresh_dpar[camtype]
                        if abs(maxthresh_dpar[camtype])!=9999:
                            dcutoff=maxthresh_dpar[camtype]
                        validpar.add((x1[-1],y1[-1]))
                        p1=np.array([x1[-1],y1[-1]])
                        p2=np.array([x2[-1],y2[-1]])
                        p1p2=(p2-p1)
                        p2b=p1+dcutoff/dpar*p1p2
                        yx1.append(p1[0])
                        yy1.append(p1[1])
                        yx2.append(p2b[0])
                        yy2.append(p2b[1])
                        ignore_for_updown=1
                if not ignore_for_updown:                
                    ds[(x1[-1],y1[-1])].append(y2[-1] - y1[-1])
            dup=dict()
            ddown=dict()
            validdownstarts=[]
            for k in ds:
                dup[k]=min(ds[k])
                if k[1]>=H/3:
                    ddown[k]=max(ds[k])
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
            for i in range(3):
                font = cv2.FONT_HERSHEY_SIMPLEX
                if i<len(_3smallest):
                    cv2.putText(image_cpy[camname], '%.2f'%_3smallest[i], (0, 100 + i * 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                if 0:
                    if 2-i<len(_3largest):
                        cv2.putText(image_cpy[camname], '%.2f' % _3largest[2-i], (0, 400 + i * 100), font, 1, (0, 255,0), 2, cv2.LINE_AA)
            if len(_3smallest) >= 3:
                mind = _3smallest[2]
            if len(_3largest) >= 3:
                maxd = _3largest[2]
            moveoff=int(camtype == 'txxx' and len(validpar)>=10)
            liftup=int(camtype == 'txxx' and mind <= minthresh[camtype])
            liftdown=int(largestdownclustersize>=3)
            cum_moveoff=int(cum_moveoff|moveoff)
            cum_liftup=int(cum_liftup|liftup)
            cum_liftdown=int(cum_liftdown|liftdown)
            cv2.putText(image_cpy[camname], f'liftup:  {cum_liftup}/{liftup}', (0, 400 + 0 * 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(image_cpy[camname], f'liftdown:{cum_liftdown}/{liftdown}', (0, 400 + 1 * 100), font, 1, (0, 255,0), 2, cv2.LINE_AA)
            cv2.putText(image_cpy[camname], f'moveoff:{cum_moveoff}/{moveoff}', (0, 400 + 2 * 100), font, 1, (0, 255,255), 2, cv2.LINE_AA)            

            for _x1, _y1, _x2, _y2 in zip(x1, y1, x2, y2):
                _x1,_y1,_x2,_y2=map(int,[_x1,_y1,_x2,_y2])
                if _y2-_y1<=minthresh[camtype]:
                    color=(0,0,255)
                elif _y1>=H/3 and _y2-_y1>=maxthresh[camtype]:
                    color=(0,255,0)
                    cv2.circle(image_cpy[camname],(_x1,_y1),100,color,1)
                else:
                    color=(255,0,0)
                cv2.arrowedLine(image_cpy[camname],(_x1,_y1),(_x2,_y2),color,2)
            #draw partial yellow line for arrow that pass min dpar length
            for _x1, _y1, _x2, _y2 in zip(yx1, yy1, yx2, yy2):
                _x1,_y1,_x2,_y2=map(int,[_x1,_y1,_x2,_y2])
                cv2.line(image_cpy[camname],(_x1,_y1),(_x2,_y2),(0,255,255),2)
            lastlinktoorigin[camname] = linktoorigin[camname]
            print(camname,3,time.time()-T0)
        else:
            try:
                sift = cv2.xfeatures2d.SIFT_create()
            except:
                sift = cv2.SIFT_create()
            lastsift[camname] = sift.detectAndCompute(image[camname], None)
            print(camname,2,time.time()-T0)
        isClosed=True
        color=(255,255,255)
        thickness=2
        cv2.polylines(image_cpy[camname], [polygon[camname]], isClosed, color, thickness)
        lastnewmask[camname] = newmask[camname]
        lastimage[camname] = image[camname]
        image_cpy[camname] = overlaymask(newmask[camname],image_cpy[camname])
        image_cpy[camname][fgmask[camname]<127]//=4
        image_cpy[camname][fgmask[camname]<127]*=3
        assignimage(imshow[camname],image_cpy[camname])
        T=time.time()
        if saveimages:
            if deploy:
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/raw/{camname}_{int((T - liftstart) * 100):06d}.jpg', image[camname])
                makedirsopen(f'{PHOTOLOGDIRNAME}/raw/colorflip_corrected.txt','w')
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/flow/{camname}_{int((T - liftstart) * 100):06d}.jpg', image_cpy[camname])
            else:
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/flow/{camname}_{Timg[camname][cami]}.jpg', image_cpy[camname])
        #if camtype == 'txxx' and (maxd >= maxthresh[camtype] or mind <= minthresh[camtype]):
        if moveoff:
            if mcrw.raw_read(f'clps_moveoffdetected_{camname}', 0) == 0:
                mcrw.raw_write(f'clps_moveoffdetected_{camname}', time.time())
                printandlog(f'{JOBDATE}_{JOBTIME},{camname},moveoff,{DATE}_{TIME}', file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                if deploy:
                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/moveoff_{DATE}_{TIME}_{camname}.jpg', image_cpy[camname])
                else:
                    makedirsimwrite(f'{PHOTOLOGDIRNAME}/moveoff_{Timg[camname][cami]}_{camname}.jpg', image_cpy[camname])
        if liftup or liftdown:
            liftdetected=1
            if mcrw.raw_read('clps_liftdetected',0)==0:
                mcrw.raw_write('clps_liftdetected',time.time())
            cornerstriggered=set()
            if camname.endswith('f'):
                cornerstriggered.update([2,3])
                mcrw.raw_write('clps_corner2',time.time())
                mcrw.raw_write('clps_corner3',time.time())
            if camname.endswith('b'):
                cornerstriggered.update([1,4])
                mcrw.raw_write('clps_corner1',time.time())
                mcrw.raw_write('clps_corner4',time.time())
            cornerstriggeredtxt='_'.join(list(str(x) for x in sorted(cornerstriggered)))
            if deploy:
                printandlog(f'{JOBDATE}_{JOBTIME},{camname},{cornerstriggeredtxt},{DATE}_{TIME}', file=makedirsopen(LOGFILENAME, 'a'), sep=",")
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}.jpg', image_cpy[camname])
            else:
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/lift_{Timg[camname][cami]}_{camname}.jpg', image_cpy[camname])
            if deploy:
                sendjson('CLPS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}.jpg')
        cami=cami+1
        
    time.sleep(3)

if __name__ == '__main__':
    Tstart = time.time()
    procimage('clpsmaskrcnn', timeout=20)
    print('init takes', time.time() - Tstart)
    print(time.time() - Tstart, file=open('/opt/captures/clpsloadtime.txt', 'a'))
    #camnames=[camnames[0]]
    if 1:
        workerpool = Pool(processes=len(camnames))
        print(camnames)
        workerpool.map(clpscam, camnames)
    else:
        clpscam('tl4xb')
    #readFrametoShm(videoinput[5])
    print("Workers launched")

