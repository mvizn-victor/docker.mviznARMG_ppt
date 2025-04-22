#version:ff13
import os
import time
from memcachehelper import memcacheRW as mcrw
from config.config import *
from Utils.helper import *
import tensorflow as tf
from tfstuff import waterdropinfer
import platform
import GPUtil
camcheckerdir='/opt/captures/camchecker'
os.makedirs(camcheckerdir,exist_ok=True)
camcheckerfile=open(f'{camcheckerdir}/log.txt','w')
tfconfig = tf.ConfigProto(
        device_count = {'GPU': 1}
    )
if len(GPUtil.getGPUs())>1:
    os.environ["CUDA_VISIBLE_DEVICES"] = '1'
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 1. / 8
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    tfconfig.gpu_options.per_process_gpu_memory_fraction = 1. / 11
def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	return cv2.Laplacian(gray, cv2.CV_64F).var()
def isblurry(image):
    return variance_of_laplacian(image)<200
def iscovered(img):
    H,W=img.shape[:2]
    #if H>W:
    #    img=cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    #H,W=img.shape[:2]
    edges = cv2.Canny(img,100,200)
    scores=[]
    for xi,yi in [[0,0],[0,.5],[.5,0],[.5,.5],[.25,.25]]:
        x1=int(xi*W//2)
        y1=int(yi*H//2)
        x2=int(xi*W//2)+W//2
        y2=int(yi*H//2)+H//2
        scores.append(np.sum(edges[y1:y2,x1:x2]>0))
    return min(scores)<100
allcams=['ovtrls','ovtrss','ovls','ovss','cnlsbf','cnlsbb','cnlsbc','tl4xb','tl20b','tl20f',
'tl4xf','pmnls','cnssbf','cnssbb','cnssbc','ts4xf','ts20f','ts20b','ts4xb','pmnss']
pmcams=['pmnls','pmnss','ovls','ovss']
cams=dict()
blur=dict()
waterdrop=dict()
for camname in allcams:
    cams[camname]=eval(camname)
    blur[camname]=0
    waterdrop[camname]=0
    if camname in ['tl20f','tl20b','tl4xf','tl4xb','ts20f','ts20b','ts4xf','ts4xb','pmnls','pmnss']:
        cams[camname].nonptzautofocus()
time.sleep(20)
os.system(f'rm {camcheckerdir}/*.jpg')
for camname in allcams:
    cams[camname].snapshot(f'{camcheckerdir}/{camname}.jpg')
time.sleep(5) 
#check water droplet for pmcams

with tf.Session(config=tfconfig, graph=waterdropinfer.graph) as sess:
    T=time.time()    
    res=waterdropinfer.get_top_res(sess, dummyimage)
    elapsed=time.time()-T
    time.sleep(max(2-elapsed,0))
    for camname in pmcams:
        imagefile=f'{camcheckerdir}/{camname}.jpg'
        if not os.path.exists(imagefile):
            waterdrop[camname]=1
        else:
            image=cv2.imread(imagefile)
            res=waterdropinfer.get_top_res(sess,image)
        if waterdrop[camname]:
            print(camname,'waterdrop',file=camcheckerfile)
#check blur for all cams
for camname in allcams:
    imagefile=f'{camcheckerdir}/{camname}.jpg'
    if not os.path.exists(imagefile):
        blur[camname]=1
    else:
        image=cv2.imread(imagefile)
        print(camname,variance_of_laplacian(image),file=camcheckerfile)
        if isblurry(image) or iscovered(image):
            blur[camname]=1
    if blur[camname]:
        print(camname,'blurry',file=camcheckerfile)
mcrw.raw_write('blur',blur)
mcrw.raw_write('waterdrop',waterdrop)
