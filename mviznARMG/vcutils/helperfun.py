#version: 1.0.5
#1.0.1
# add replace_suffix
#1.0.2
# add ipyshow similar to ??, ipyrun similar to %run -i
# prevent run fail when some packages such as numpy and cv2 not installed, generally still usable with minimal packages installed
#1.0.3
# progress do
#1.0.4
# filter_dict_by_keys
# conversion between pil and cv2
# rect_intersection, arearect from endfeed hpds
#1.0.5
# fix defaultprint=__builtins__.print or __builtins__['print']
try:
    helperfunipy
except:
    helperfunipy='~/helperfun.ipy'
class MyExc(Exception):
    pass

def rect_intersection(rect1, rect2):
    # Unpack the rectangles
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculate the edges of the rectangles
    left1, right1, top1, bottom1 = x1, x1 + w1, y1, y1 + h1
    left2, right2, top2, bottom2 = x2, x2 + w2, y2, y2 + h2

    # Find overlap
    overlap_left = max(left1, left2)
    overlap_right = min(right1, right2)
    overlap_top = max(top1, top2)
    overlap_bottom = min(bottom1, bottom2)

    # Check if there is an intersection
    if overlap_left < overlap_right and overlap_top < overlap_bottom:
        # Calculate the top-left corner, width, and height of the intersection
        overlap_width = overlap_right - overlap_left
        overlap_height = overlap_bottom - overlap_top
        return (overlap_left, overlap_top, overlap_width, overlap_height)
    else:
        # No intersection
        return (0, 0, 0, 0)

def arearect(rect):
    return rect[2]*rect[3]

def calc_iou(rect1,rect2):
    overlap=rect_intersection(rect1,rect2)
    return arearect(overlap)/max(arearect(rect1)+arearect(rect2)-arearect(overlap),1e-6)

def filter_dict_by_keys(source_dict, keys_to_extract):
    """
    Returns a new dictionary containing only the key-value pairs from source_dict
    whose keys are present in keys_to_extract.
    
    Parameters:
    - source_dict (dict): The original dictionary.
    - keys_to_extract (iterable): Keys to filter from the dictionary.

    Returns:
    - dict: A filtered dictionary.
    """
    return {k: source_dict[k] for k in keys_to_extract if k in source_dict}

def pil_to_cv2(pil_image):
    import cv2
    import numpy as np
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
def cv2_to_pil(cv2_image):
    import cv2
    from PIL import Image
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

def ipyshow(obj):
    try:
        source = inspect.getsource(obj)
        print("🔍 Source code:\n")
        print(source)
    except TypeError:
        print("❌ Source code not available.")
    
    doc = inspect.getdoc(obj)
    if doc:
        print("\n📘 Docstring:\n")
        print(doc)
    else:
        print("\n⚠️ No docstring found.")
def ipyrun(f,env=None):
    if env is None:
        env=globals()
    exec(open(f).read(),env)

def displaycv2(img):
    import cv2
    import io
    from IPython.display import display, Image
        
    # Convert from BGR to RGB if you want the correct colors
    #img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Encode the image as PNG
    success, encoded_image = cv2.imencode('.png', img)
    if success:
        # Create a bytes buffer from the encoded image
        image_bytes = io.BytesIO(encoded_image)
        # Display the image using IPython.display.Image
        display(Image(data=image_bytes.getvalue()))
    else:
        print("Failed to encode image")

def replace_suffix(string, old_suffix, new_suffix):
    if not string.endswith(old_suffix):
        raise ValueError(f"String does not end with '{old_suffix}'")
    return string[:-len(old_suffix)] + new_suffix

def printtime(*x,**kw):
    from datetime import datetime
    if 1 or 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    defaultprint(*x,**kw)


def normcolname(x):
    import re
    x=x.replace(' ','_')
    x=re.sub('[^a-zA-Z0-9_]','_',x)
    x=x.strip('_')
    x=re.sub('_+','_',x)
    return x

def drawpoly(im, points, color=(0, 255, 255), thickness=1):
    # Create a black image
    points=np.int_(np.float_(points))
    # Reshape the points array to be a 1 x n x 2 array
    pts = points.reshape((-1, 1, 2))

    # Draw the polygon on the image
    cv2.polylines(im, [pts], True, color, thickness)

def assigndkv(d,ktuple,v):
    dd=d
    dd0=None
    k0=None
    for k in ktuple[:-1]:
        try:
            dd[k]
        except:
            if isinstance(k,int):
                if not isinstance(dd0[k0],list):
                    dd0[k0]=[]
                    dd=dd0[k0]
                while len(dd)<k+1:
                    dd.append({})
            else:
                dd[k]={}
        dd0=dd
        k0=k
        dd=dd[k]
    k=ktuple[-1]
    dd[k]=v

def cp(s):
    """
    write to /tmp/S for vim to paste
    """
    print(s,file=open('/tmp/S','w'))

def assigndkv(d,ktuple,v):
    """
    helper function to build json
    """
    dd=d
    dd0=None
    k0=None
    for k in ktuple[:-1]:
        try:
            dd[k]
        except:
            if isinstance(k,int):
                if not isinstance(dd0[k0],list):
                    dd0[k0]=[]
                    dd=dd0[k0]
                while len(dd)<k+1:
                    dd.append({})
            else:
                dd[k]={}
        dd0=dd
        k0=k
        dd=dd[k]
    k=ktuple[-1]
    dd[k]=v

def grep(pat,l__x,filter=lambda s:s[:2]!='__'):
    out=[]
    for s in sorted(l__x):
        if filter(s):
            if re.match(pat,s):
                out.append(s)
    return out

def rglob(s,prefix='',n=10,t=10,p=1):
    "t=max duration,n=max hit,p=print"
    ls=s.split("/")
    T0=time.time()
    out=[]
    while 1:
        if n<=0:break
        if time.time()-T0>t:
            print("time's up")
            break
        try:
            ls2=list(ls)
            for i,s2 in enumerate(ls):
                if s2=='':continue
                if i>0:
                    prefix2=prefix+"/".join(ls2[:i])+"/"
                else:
                    prefix2=prefix
                ls3=glob.glob(f"{prefix2}{s2}")
                s3=random.choice(ls3)
                ls2[i]=s3.split("/")[i]
            prefix2=prefix+"/".join(ls2)
            if prefix2 not in out:
                if p:print(prefix2)
                out.append(prefix2)
            n-=1
        except kbi:
            raise
        except:
            pass
    return out
def br(s):
    "bash resolve"
    return os.popen(f"echo {s}").read().strip()


class myobject:
    pass
def voidfun(*args,**kwargs):
    pass
def getYmdHMSf(NOW=None):
    if NOW is None:
        NOW=datetime.now()
    return NOW.strftime('%Y-%m-%d_%H-%M-%S.%f')
def getYmdHMS(NOW=None):
    if NOW is None:
        NOW=datetime.now()
    return NOW.strftime('%Y-%m-%d_%H-%M-%S')
def getYmdHM(NOW=None):
    if NOW is None:
        NOW=datetime.now()
    return NOW.strftime('%Y-%m-%d_%H-%M')
from threading import Thread
def threadcopy(src,dest):
    thread = Thread(target=shutil.copy, args=(src,dest), daemon=True)
    thread.start()
def resizefit(frame,target=(1920,1080)):
    """
    s=scale
    """
    h,w=frame.shape[:2]
    wtarget,htarget=target
    #htarget=int(1080*s)
    #wtarget=int(1920*s)
    scale=min(wtarget/w,htarget/h)
    return cv2.resize(frame,(int(scale*w),int(scale*h)))


class C__rect:
    """
    inputformat:
    x1y1wh
    x1y1x2y2
    xcycwh
    
    outputformat:
    xcyc
    x1y1x2y2
    x1y1wh
    xcycwh
    
    int-> make every ent
    """
    __version__=2
    def __init__(self,rect,format='x1y1wh'):
        if format=='x1y1wh':
            self.x1,self.y1,self.w,self.h=rect
        elif format=='x1y1x2y2':
            self.x1,self.y1,self.x2,self.y2=rect
            self.w=self.x2-self.x1
            self.h=self.y2-self.y1
        elif format=='xcycwh':
            self.xc,self.yc,self.w,self.h=rect
            self.x1=self.xc-self.w/2
            self.y1=self.yc-self.h/2
    def int(self):
        self.x1,self.y1,self.w,self.h=map(lambda x:int(round(x)),[self.x1,self.y1,self.w,self.h])
        return self
    def xcyc(self):
        xc=self.x1+self.w/2
        yc=self.y1+self.h/2
        return xc,yc
    def x1y1x2y2(self):
        x1=self.x1
        y1=self.y1
        x2=self.x1+self.w
        y2=self.y1+self.h
        return x1,y1,x2,y2
    def x1y1wh(self):
        x1=self.x1
        y1=self.y1
        w=self.w
        h=self.h
        return x1,y1,w,h
    def xcycwh(self):
        xc=self.x1+self.w/2
        yc=self.y1+self.h/2
        w=self.w
        h=self.h
        return xc,yc,w,h
    #version=2
    def crop(self,frame):
        return frame[max(0,self.y1):max(0,self.y2),self.x1:self.x2]
    def __str__(self):
        return f'{self.x1} {self.y1} {self.x2} {self.y2}'
    def __repr__(self):
        return self.__str__()
    

    
def reflectim(im,c='I'):
    if c=='H':
        im=im[:,::-1]
    elif c=='V':
        im=im[::-1,:]
    elif c=='HV':
        im=im[::-1,::-1]
    return im
def reflectrect(im,rect,c='I'):
    H,W=im.shape[:2]
    rectx1,recty1,rectw,recth=rect
    _rectx1,_recty1,_rectw,_recth=rect
    if c=='H':
        _rectx1=W-rectx1-rectw
    elif c=='V':
        _recty1=H-recty1-rectH
    elif c=='HV':
        _rectx1=W-rectx1-rectw
        _recty1=H-recty1-rectH
    return (_rectx1,_recty1,_rectw,_recth)
def hstack(list_im):
    maxw=max(im.shape[1] for im in list_im)
    maxh=max(im.shape[0] for im in list_im)
    list_im2=[]
    for im in list_im:
        #pad
        h,w=im.shape[:2]
        im=np.vstack([im,np.zeros((maxh-h,w,3),np.uint8)])
        list_im2.append(im)
    return np.hstack(list_im2)
def vstack(list_im):
    maxw=max(im.shape[1] for im in list_im)
    maxh=max(im.shape[0] for im in list_im)
    list_im2=[]
    for im in list_im:
        #pad
        h,w=im.shape[:2]
        im=np.hstack([im,np.zeros((h,maxw-w,3),np.uint8)])
        list_im2.append(im)
    return np.vstack(list_im2)
def getvalue(x):
    #x is stringio
    #x is filename
    #x is writables
    try:
        return x.getvalue()
    except:
        pass
    try:
        return open(x).read()
    except:
        pass

try:
    defaultprint=__builtins__.print
except:
    defaultprint=__builtins__['print']

    
def printfile(filename=None,mode='w',prefixfun=lambda:''):
    """example
    logfile0=makedirsf('/opt/captures/logs/efyolo.txt')
    logfile1=io.StringIO()
    print0=printfile(logfile0,'a')
    while ...
        try:
            print1=printfile(logfile1,'w')
            print1()
            ...
        except:
            print0()
            
    """
    if mode not in ['a','w']:
        print('printfile')
        print('filename=',filename)
        print('mode=',mode)
        print('mode must be a or w')
        raise kbi
    if filename is None:
        return defaultprint
    isfile=0
    try:
        #if can getvalue, then is stringio
        filename.getvalue()
        file=filename
        isfile=1
        if mode=='w':
            file.truncate(0)
    except:
        pass
    try:
        #if can write, then is file type
        filename.write('')
        file=filename
        isfile=1
    except:
        if not isfile:
            if mode=='w':
                file=open(filename,mode)
                isfile=1
    def print1(*args,**kwargs):
        nonlocal isfile,file,prefixfun
        if not isfile:
            if mode=='a':
                file=open(filename,mode)
                isfile=1
        kwargs['file']=file
        defaultprint(prefixfun(),end=' ')
        defaultprint(*args,**kwargs)
        file.flush()
    return print1

def printdef():
    print(os.popen('grep "^def" {helperfunipy}|sort;grep "^class" {helperfunipy}|sort').read())
    found=0
    for line in open(os.path.expanduser(helperfunipy)):
        if line=='#constants\n':
            found=1
        if found and '=' in line:
            print(line,end="\n")
try:
    helperfunprint
except:
    helperfunprint=0
if helperfunprint:
    print('to disable printing: helperfunprint=0')
    
kbi=KeyboardInterrupt
import traceback
def printerror(e,file=None,print=None):
    if print is None:
        print=defaultprint

    print("An exception occurred:", e,file=file)
    print("\nStack trace:",file=file)
    print(traceback.format_exc(),file=file)
import io
from collections import defaultdict
import pickle
import time
from datetime import datetime,timedelta
import sys
import os
import glob
import re
import shutil
import random
import subprocess

_main = sys.modules['__main__']

try:
    import numpy as np
    dummyimage=np.zeros([3,3,3],dtype=np.uint8)
except:
    dummyimage=None
    if helperfunprint:
        print('pip install numpy')    
try:    
    from PIL import Image
except:
    if helperfunprint:
        print('pip install PIL')
try:    
    from IPython.display import clear_output
except:
    if helperfunprint:
        print('pip install jupyterlab')
try:        
    import pandas as pd
except:
    if helperfunprint:
        print('pip install pandas')    
try:
    import cv2
except:
    class Obj:
        def __getattr__(self,name):
            pass
    cv2=Obj()
    if helperfunprint:
        print('pip install opencv-python')

class GM: 
    #globals manager    
    k=[]
    G=dict()
    def keys():
        import inspect
        frame=inspect.currentframe().f_back        
        G=globals()
        L=dict()
        while frame.f_locals is not G:
            L.update(frame.f_locals)
            frame=frame.f_back
        return sorted(list(L.keys())+list(G.keys()))
    def Locals():
        import inspect
        frame=inspect.currentframe().f_back        
        G=globals()
        L=dict()
        while frame.f_locals is not G:
            L.update(frame.f_locals)
            frame=frame.f_back
        return L
    def push(L=dict()):
        import inspect
        frame=inspect.currentframe().f_back        
        G=globals()
        while frame.f_locals is not G:
            L.update(frame.f_locals)
            frame=frame.f_back
        GM.k=list(L.keys())
        GM.G=dict()
        for k in L:
            if k in G:
                GM.G[k]=L[k]
            G[k]=L[k]
    def pop():
        G=globals()
        for k in GM.k:
            if k in GM.G:
                G[k]=GM.G[k]
            else:
                try:
                    del G[k]
                except:
                    pass
        GM.k=[]

def setkv(d,k,v):
    if type(k)==tuple:
        d2=d
        for k2 in k[:-1]:
            if k2 not in d2:
                d2[k2]=dict()
            d2=d2[k2]
        d2[k[-1]]=v
    else:
        d[k]=v
def getk(d,k):
    if type(k)==tuple:
        d2=d
        for k2 in k:
            if k2 not in d2:
                return None
            d2=d2[k2]
        return d2
    else:
        if k not in d:
            return None
        return d[k]
def chunk_string(string, max_size):
    """
    Splits a given string into chunks of a maximum size.
    :param string: The string to split into chunks.
    :param max_size: The maximum size of each chunk.
    :return: A list of chunks.
    """
    return [string[i:i+max_size] for i in range(0, len(string), max_size)]
def is_primitive(variable):
    primitive_types = (int, float, bool, str, bytes)    
    return isinstance(variable, primitive_types)
def strx(x):
    if is_primitive(x):
        return x
    else:
        return strtypex(x)
def strtypex(x):
    return 'type:'+type(x).__name__
def printlevel(d,level,n=10,prefix=()):
    #print('printlevel',d,level,n,prefix)
    if level==0:
        print(prefix,strx(d))
        return n-1
    if level==1 and isinstance(d,list):
        i=0
        while n>0 and i<len(d):
            print(prefix,f'[{i}]',strx(d[i]))
            n-=1
            i+=1
    if isinstance(d,dict):
        for k in d:
            if n<=0:break
            n=printlevel(d[k],level-1,n,prefix=prefix+(k,))
    return n
def printlevels(d,n=10,maxlevel=10):
    for level in range(1,maxlevel):
        print('\nlevel',level)
        nn=printlevel(d,level=level,n=n)
        #print('nn',nn)
        if nn==n:break


def globslice(s,n=20):
    out=[]
    for i,x in enumerate(glob.iglob(s)):
        out.append(x)
        if i==n-1:
            break
    return out

def makedirsf(f):
    os.makedirs(os.path.dirname(f),exist_ok=True)
    return f

def spacedsampleI(N,n):
    if n>=N:return np.array(range(N))
    else:
        return np.int64(np.round(N/(n+1)*np.array(range(1,n+1))+.49))-1
    
def spacedsample(X,n):
    out=[]
    for i in spacedsampleI(len(X),n):
        out.append(X[i])
    return out

def natural_sort_key(x):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return alphanum_key(str(x))

def natural_sort(l):
    return sorted(l, key = natural_sort_key)

import os
def checkabort():
    abortfile=f'/dev/shm/abort{_main.abortid}'
    if os.path.exists(abortfile):
        unlink(abortfile)
        raise KeyboardInterrupt
def run(command):
    checkabort()
    ret=os.system(command)
    if ret!=0:raise Exception(f'runfail: {command}')
def extractimage(vidfile,hstart,minstart,secstart,duration,Fout):
    #glob.glob(Fout.replace('%06d','*'))
    command=f'ffmpeg -y -ss {hstart}:{minstart}:{secstart} -i {vidfile} -t {duration} -c copy /tmp/1.mp4'
    run(command)
    command=f'ffmpeg -i /tmp/1.mp4 -vf fps=20  {Fout}'
    run(command)    
    return sorted(glob.glob(Fout.replace('%06d','*')))
def extractimage1(vidfile,start,Fout):
    command=f'ffmpeg -y -ss {start} -i {vidfile}  -vframes 1 {Fout}'
    run(command)
def unlink(f):
    try:
        os.unlink(f)
    except KeyboardInterrupt:
        raise
    except:
        pass
def imreadextractimage1(vidfile,start):
    unlink('/dev/shm/extractimage.jpg')
    extractimage1(vidfile,start,'/dev/shm/extractimage.jpg')
    if not os.path.exists('/dev/shm/extractimage.jpg'):
        raise Exception()
    return cv2.imread('/dev/shm/extractimage.jpg')
def imswk(frame,t=0,name='xxx',s=0.8):
    """
    s=scale
    """
    h,w=frame.shape[:2]
    htarget=int(1080*s)
    wtarget=int(1920*s)
    scale=min(wtarget/w,htarget/h)
    cv2.namedWindow(name)
    def doclick(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:        
            print(x/scale,y/scale,w,h,file=open('/tmp/out.txt','a'))
    cv2.setMouseCallback(name, doclick)
    cv2.imshow(name,cv2.resize(frame,(int(scale*w),int(scale*h))))
    k=cv2.waitKey(t)
    if k==ord('q'):
        cv2.destroyAllWindows()
        raise KeyboardInterrupt
    return k
def daw():
    cv2.destroyAllWindows()
def eograndomn(d,n=100): 
    x=glob.glob(f'{d}/*.jpg')
    import random
    random.shuffle(x)
    os.system("eog {' '.join(x[:n])}")
def makedirsf(f):
    if os.path.dirname(f)!='':
        os.makedirs(os.path.dirname(f),exist_ok=True)    
        
def imshow(frame):    
    cv2.imwrite('/tmp/1.jpg',frame)
    os.system("eog /tmp/1.jpg        ")
    
def imshow_resize(frame):
    cv2.imwrite('/tmp/1.jpg',cv2.resize(frame,(800,800)))
    os.system("eog /tmp/1.jpg        ")
    

def imshowpil(pil_im):
    return plt.imshow(np.asarray(pil_im))
def imshowcv(cv2_im):
    if len(cv2_im.shape)==3:
        return plt.imshow(cv2_im[:,:,::-1])
    else:
        return plt.imshow(cv2_im)
def imshowfile(f):
    imshowcv(cv2.imread(f))
    
def pil2cv(pil_image):
    return np.array(pil_image)[:,:,::-1].copy()
def stripimage(frame):
    H,W=frame.shape[:2]
    #x,y,w,h=cv2.boundingRect(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    x,y,w,h=cv2.boundingRect(frame)
    x2=x+w
    y2=y+h
    x=max(0,x-2)
    y=max(0,y-2)
    x2=x2+2
    y2=y2+2
    return frame[y:y2,x:x2]    

def geti0(i):
    try:
        return i[0]
    except:
        return i
class Inception:
    def __init__(self,pbfile,labelsfile=None):
        if labelsfile is None:
            labelsfile=pbfile[:-3]+'.labels'
        self.net=cv2.dnn.readNet(pbfile)
        self.classes=open(labelsfile).read().rstrip().split('\n')
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        tmp = self.net.getLayerNames()    
        self.ln=[]
        for i in self.net.getUnconnectedOutLayers():
            self.ln.append(tmp[geti0(i)-1]) 
    def infer(self,frame):
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (299, 299),
                swapRB=True, crop=False)
        self.net.setInput(blob)
        self.layerOutputs = self.net.forward(self.ln)
        res = np.squeeze(self.layerOutputs)
        i = np.argmax(np.squeeze(self.layerOutputs))
        return self.classes[i],res[i]
class YOLO:
    def __init__(self,weightsfile,cfgfile=None,namesfile=None,size=None):
        if cfgfile is None:
            cfgfile=weightsfile[:-len('.weights')]+'.cfg'            
        if namesfile is None:
            namesfile=weightsfile[:-len('.weights')]+'.names'
        cfg=dict()
        for line in open(cfgfile):
            if '#' in line:continue
            try:
                k,v=line.strip().split('=')[:2]
                cfg[k]=v
            except:
                pass
        if size is None:
            size=(int(cfg['width']),int(cfg['height']))
        self.net=cv2.dnn.readNet(weightsfile, cfgfile)
        self.classes=open(namesfile).read().rstrip().split('\n')
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(size=size, scale=1/255)
    def infer(self, frame, CONFIDENCE_THRESHOLD=0.2, NMS_THRESHOLD=0.4):
        classes, scores, boxes = self.model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        classes = list(self.classes[geti0(i)] for i in classes)
        scores = list(geti0(score) for score in scores)
        return classes, scores, boxes
    def inferold(self, frame, thresh=0.2):
        classes, scores, boxes = self.infer(frame, thresh)
        results = []
        for (classid, score, box) in zip(classes, scores, boxes):
            result=['',0,[0,0,0,0]]
            result[0]=classid
            result[1]=score
            box[0]=box[0]+box[2]/2
            box[1]=box[1]+box[3]/2
            result[2]=box
            results.append(result)
        return results


def myhash(s):
    import hashlib
    return hashlib.md5(s.encode('utf8')).hexdigest()
    
def iglob(s,i=1):
    out=[]
    for x in glob.iglob(s):
        out.append(x)
        if len(out)>=i:
            break
    return out

def replaceassert(s,a,b):
    s2=s.replace(a,b)
    assert(s!=s2 or a==b)
    return s2

def get_length(filename):
    """
    get video length
    """
    import subprocess
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
    
class Progress:    
    def __init__(self,interval=1,multiplier=1):
        self.lastT_hardnotify=0
        self.lastT=0
        self.interval=interval
        self.multiplier=multiplier
    def do(self,fun):
        import time
        if time.time()-self.lastT>self.interval:
            fun()
            self.lastT=time.time()
            self.interval*=self.multiplier

    def print(self,*s):
        import time
        if time.time()-self.lastT>self.interval:
            print(*s)
            self.lastT=time.time()
            self.interval*=self.multiplier
    def notify(self,*s):
        import time
        if time.time()-self.lastT>self.interval:
            os.system(f'softnotify.py "{s[0]}"')
            self.lastT=time.time()
            self.interval*=self.multiplier            
    def printandnotify(self,*s):
        import time
        if time.time()-self.lastT>self.interval:
            print(*s)
            os.system(f'softnotify.py "{s[0]}"')
            self.lastT=time.time()
            self.interval*=self.multiplier
            
    def hardnotify(self,*s):
        import time
        if time.time()-self.lastT_hardnotify>10:
            os.system(f'notify.py "{s[0]}"')
            self.lastT_hardnotify=time.time()
            self.interval*=self.multiplier            

def procimage(procname,img=dummyimage,timeout=10):
    T=time.time()
    os.makedirs(f'/dev/shm/{procname}/',exist_ok=True)
    cv2.imwrite(f'/dev/shm/{procname}/{T}.jpg',img)
    fout=f'/dev/shm/{procname}/{T}.pkl'
    while True:
        if time.time()-T>=timeout:
            raise Exception('procimage',procname,'timeout')
        try:
            res=pickle.load(open(fout,'rb'))
            os.unlink(fout)
            break
        except:
            time.sleep(0.001)
    return res

def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
def rounded_rectangle(src, top_left, bottom_right, radius=1, color=255, thickness=1, line_type=None):
    if line_type is None:
        line_type=cv2.LINE_AA

    #  corners:
    #  p1 - p2
    #  |     |
    #  p4 - p3

    p1 = (top_left[0],top_left[1])
    p2 = (bottom_right[0], top_left[1])
    p3 = (bottom_right[0], bottom_right[1])
    p4 = (top_left[0], bottom_right[1])

    height = abs(bottom_right[1] - top_left[1])

    if radius > 1:
        radius = 1

    corner_radius = int(radius * (height/2))

    if thickness < 0:

        #big rect
        top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
        bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

        top_left_rect_left = (p1[0], p1[1] + corner_radius)
        bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

        top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
        bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

        all_rects = [
        [top_left_main_rect, bottom_right_main_rect], 
        [top_left_rect_left, bottom_right_rect_left], 
        [top_left_rect_right, bottom_right_rect_right]]

        [cv2.rectangle(src, rect[0], rect[1], color, thickness) for rect in all_rects]

    # draw straight lines
    cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
    cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
    cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
    cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, color ,thickness, line_type)
    cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, color , thickness, line_type)
    cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,   color , thickness, line_type)
    cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,  color , thickness, line_type)

    return src    

def putText(frame,text,position,thickness=1,color=(255,0,0),font_scale=1,font =  cv2.FONT_HERSHEY_SIMPLEX,line_type = cv2.LINE_AA,shadow=0):
    WHITE=(255,255,255)
    text_size, _ = cv2.getTextSize(text,  cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    line_height = text_size[1] + 5
    x, y0 = position
    for i, line in enumerate(text.split("\n")):            
        y = y0 + i * line_height
        if shadow:
            cv2.putText(frame,
                        line,
                        (x+thickness, y+thickness),
                        font,
                        font_scale,
                        WHITE,
                        thickness,
                        line_type)
        cv2.putText(frame,
                    line,
                    (x, y),
                    font,
                    font_scale,
                    color,
                    thickness,
                    line_type)
    

def findkey(self,s1):
    """g.findkey(s1) to search key containing s1"""
    return sorted(list(s for s in dir(self) if s[0]!='_' and s1.lower() in s.lower()),key=lambda x:x.lower())

def makedirsf(f):
    os.makedirs(os.path.dirname(f),exist_ok=True)
    return f

class MyVideoWriter:
    """
vidout=MyVideoWriter(fname='out.mp4',fps=5)
for i in range(5):
    vidout.write(im)
vidout.release()
    """
    def __init__(self,fname,fps):
        self.vidh=None
        self.vidw=None
        self.VideoWriter=None
        self.fname=fname
        self.fps=fps
    def write(self,frame):
        if self.VideoWriter is None:
            h,w=frame.shape[:2]
            htarget=720
            wtarget=1280
            scale=min(wtarget/w,htarget/h)
            self.vidh,self.vidw=(int(scale*h),int(scale*w))
            fourcc=cv2.VideoWriter_fourcc(*"MP4V")
            self.VideoWriter=cv2.VideoWriter(makedirsf(self.fname),fourcc,self.fps,(self.vidw,self.vidh))
        self.VideoWriter.write(cv2.resize(frame,(self.vidw,self.vidh)))
    def release(self):
        try:
            self.VideoWriter.release()
        except:
            pass

def myglob(pattern):
    return sorted(x.rstrip('/') for x in sorted(glob.glob(pattern)))

def gencollage(list_im,rows=0,cols=0):
    N=len(list_im)
    if cols>0 and rows==0:
        rows=(N+cols-1)//cols
    elif rows>0 and cols==0:
        cols=(N+rows-1)//rows
    else:
        cols=N
        rows=1
    for i in range(N):
        im=list_im[i]
        if im is None:
            list_im[i]=np.zeros((1,1,3),dtype=np.uint8)
    maxw=max(im.shape[1] for im in list_im)
    maxh=max(im.shape[0] for im in list_im)
    collage=np.zeros((rows*maxh,cols*maxw,3),dtype=np.uint8)
    for i in range(N):
        row=i//cols
        col=i%cols
        im=list_im[i]
        h,w=im.shape[:2]
        collage[maxh*row:maxh*row+h,maxw*col:maxw*col+w]=im
    return collage

#procimage

def procimage(procname,img=dummyimage,timeout=10):
    T=time.time()
    os.makedirs(f'/dev/shm/{procname}/',exist_ok=True)
    cv2.imwrite(f'/dev/shm/{procname}/{T}.jpg',img)
    fout=f'/dev/shm/{procname}/{T}.pkl'
    while True:
        if time.time()-T>=timeout:
            raise Exception('procimage',procname,'timeout')
        try:
            res=pickle.load(open(fout,'rb'))
            os.unlink(fout)
            break
        except:
            time.sleep(0.001)
    return res

def waittillvalidimage(f,timeout=0.1):
    T=time.time()
    while True:
        if time.time()-T>=timeout:
            print('timeout', time.time() - T)
            return 0
        try:            
            if open(f,'rb').read()[-2:]==b'\xff\xd9':
                print('waited',time.time()-T)            
                return 1
        except:
            pass
        time.sleep(0.001)



#constants
rainbowbgr=[(0, 0, 255),
 (0, 165, 255),
 (0, 255, 255),
 (0, 128, 0),
 (255, 0, 0),
 (130, 0, 75),
 (238, 130, 238),
 (128, 128, 128),
 (255, 255,255),
]
rainbowrgb=[(255, 0, 0),
 (255, 165, 0),
 (255, 255, 0),
 (0, 128, 0),
 (0, 0, 255),
 (75, 0, 130),
 (238, 130, 238),
 (128, 128, 128),
 (255, 255,255),
]
rainbownames=['red','orange','yellow','green','blue','indigo','violet','gray','white']
rainbowrgbhex=['#ff0000', '#ffa500', '#ffff00', '#008000', '#0000ff', '#4b0082', '#ee82ee','#808080','#FFFFFF']
helperfunipy=helperfunipy
helperfunprint=helperfunprint
