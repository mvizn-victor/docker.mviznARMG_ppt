#version:1
#!
import sys
import re
from multiprocessing import Pool
import cv2
import time
import numpy as np
import SharedArray as sa
import socket
from config.config import *
from memcachehelper import memcacheRW as mcrw
import os
#from cronus.timeout import timeout, TimeoutError
import requests
from requests.auth import HTTPDigestAuth
import cv2
import numpy as np
import camDriverRaw
class CamSession:
    """
    Handles camera comm over http
    Uses jpg snapshot
    """

    def __init__(self,
                 cam_url,
                 cam_uname,
                 cam_passwd
                 ):

        self.camUrl = cam_url
        self.auth = HTTPDigestAuth(cam_uname, cam_passwd)
        self.session = requests.session()

    def get_img(self):
        http_response = self.session.get(self.camUrl, auth=self.auth, timeout=0.7)
        cv_img = np.asarray(bytearray(http_response.content), dtype="uint8")
        cv_img = cv2.imdecode(cv_img, cv2.IMREAD_COLOR)
        return cv_img



class MyVideoCapture:
    SELF = None
    def __init__(self,link,**params):
        if link.find("::")>=0:
            username,password,link = link.split('::')
            self.SELF = CamSession(link,username,password)
            self.type = 'CamSession'
            if 'fps' in params:
                self.fps=params['fps']
            else:
                self.fps=5
        #elif link[:1]=="!":
        elif False:
            link=link[1:]
            #eg root:123456@192.168.1.13
            link=f'souphttpsrc timeout=1 location=http://{link}/axis-cgi/mjpg/video.cgi?fps={self.fps} ! jpegdec ! videoconvert ! appsink '
            self.SELF = cv2.VideoCapture(link,cv2.CAP_GSTREAMER)
            self.type = 'VideoCapture'
        elif link.endswith('.jpg'):
            self.SELF = cv2.imread(link)
            self.type = 'Image'
        else:
            self.SELF = cv2.VideoCapture(link)
            self.type = 'VideoCapture'
    def read(self):
        if self.type == 'VideoCapture':
            return self.SELF.read()
        elif self.type == 'Image':
            return True,self.SELF
        else:
            T=time.time()
            for i in range(3):
                try:
                    frame = self.SELF.get_img()
                    ret = True
                    break
                except Exception as e:
                    print(self.SELF.camUrl,'FAIL',i+1)
                    time.sleep(max(0,0.7-(time.time()-T)))
                    frame = None
                    ret = False
            return ret, frame
    def seekframe(self,framenum):
        return self.SELF.set(1,framenum)
    def seektime(self,msec):
        return self.SELF.set(0,msec)
    def release(self):
        if self.type == 'VideoCapture':
            return self.SELF.release()
#@timeout(1)
def readcap(cap):
    return cap.read()

#@timeout(2) #somehow sleep freezes and doesn't return without this
def sleep1():
    #return time.sleep(1)
    pass
def createShmRawFrame(camid, shape, dtype):
    try:
        fbasename = f"{camid}_raw"
        if os.path.exists(f'/dev/shm/{fbasename}'):
            os.unlink(f'/dev/shm/{fbasename}')
        fname = f"shm://{fbasename}"
        sa.create(fname, shape, dtype=dtype)
        print(fname, "created")
    except FileExistsError:
        print(fname, "already exists")
    finally:
        shmarray = sa.attach(fname)
        return shmarray
def createShmYoloFrame(camid, shape, dtype):
    try:
        fbasename = f"{camid}_yoloframe"
        if os.path.exists(f'/dev/shm/{fbasename}'):
            os.unlink(f'/dev/shm/{fbasename}')
        fname = f"shm://{fbasename}"
        sa.create(fname, shape, dtype=dtype)
        print(fname, "created")
    except FileExistsError:
        print(fname, "already exists")
    finally:
        shmarray = sa.attach(fname)
        return shmarray


def readFrametoShm(videoinfo):
    camid=videoinfo[0]
    input_video = videoinfo[1]
    if len(videoinfo)>=3:
        w, h = videoinfo[2]
    else:
        w, h = 1280,720
    mcrw.raw_write('%slastrawupdate'%camid,0)

    firstrun = True
    #w,h=1920,1080
    shape = (h, w, 3)
    frame = np.zeros(shape, np.uint8)
    shmarray_raw = createShmRawFrame(camid, frame.shape, frame.dtype)
    shmarray_yoloframe = createShmYoloFrame(camid, frame.shape, frame.dtype)
    if input_video[:1]=="!":
        try:
            uname,passwd,ip,fps=re.match('!(.*):(.*)@(.*):(.*)',input_video).groups()
        except:
            uname,passwd,ip=re.match('!(.*):(.*)@(.*)',input_video).groups()
            fps=5
        #print(uname,passwd,ip)
        camDriverRaw.FrameGrabber(f'http://{ip}/axis-cgi/mjpg/video.cgi?fps={fps}&resolution={w}x{h}',uname,passwd,shmarray_raw,camid).run()
        #ip1,ip2=ip.rsplit('.',1)
        #device=int(ip2)-130
        #camDriverRaw.FrameGrabberRTSP(f"rtsp://{ip1}.130/{device}",shmarray_raw,camid).run()
    else:
        while True:
            #print(f"DEBUG:{camid} 1")
            if firstrun or cap.type == 'VideoCapture':
                cap = MyVideoCapture(input_video)
                #print(f'{camid} {isinstance(cap,cv2.VideoCapture)}')
            try:
                if cap.type=='VideoCapture':cap.seektime((60*0+0)*1000)
                ret, frame = readcap(cap)
                if firstrun:print(frame.shape,file=open(f'/tmp/{camid}frameshape','w'))
                pass
            except Exception as e:
                print(f"DEBUG:{camid} 2 Exception:{e}")
                ret = 0
            if ret:
                mcrw.raw_write('%slastrawupdate'%camid,time.time())
                mcrw.raw_write('%sok'%camid,1)
            else:
                mcrw.raw_write('%sok'%camid,0)
            firstrun = False
            #smallshape = (270, 480, 3)
            #smallshape = (512, 512, 3)  #same as CNN input shape
            #shmarray_small = createShmSmallFrame(camid, smallshape, frame.dtype)
            i = 0
            while ret:

                i += 1
                # Capture frame-by-frame
                t1=time.time()
                try:
                    ret, frame = readcap(cap)
                except:
                    print(f"DEBUG:{camid} 3: {time.time() - t1}")
                    ret = 0
                t2=time.time()
                if ret:
                    mcrw.raw_write('%slastrawupdate'%camid,time.time())
                    #frame_small = cv2.resize(frame, dsize=(smallshape[1], smallshape[0]))
                    if frame.shape!=shape:
                        frame = cv2.resize(frame, dsize=(shape[1], shape[0]))
                    np.copyto(shmarray_raw, frame)
                    #np.copyto(shmarray_small, frame_small)

                t3=time.time()
                #time.sleep(max(0, (0.2 -(t3-t1))))
                time.sleep(max(0, (0.01 - (t3 - t1))))
                #time.sleep(max(0, (1/24 - (t3 - t1))))
                t4=time.time()
                #if i%100 == 0:
                #    print(camid, "Read frame from cam:", (t2 - t1), " Resized & wrote frame to RAM:", (t3 - t2), " Slept:", max(0, (0.1 -(t3-t1))), " Total:", (t4-t1  ))
            #if not ret:
            shmarray_raw[:]=0
            mcrw.raw_write('%sok' % camid, 0)
            cap.release()
            time.sleep(1)

if __name__ == '__main__':
    videoinput2=[]
    os.system('rm /dev/shm/*_raw')
    if len(sys.argv)>1:
        if sys.argv[1]=='l':
            #stream landside only    
            for x in videoinput:
                if 'l' not in x[0] and 'ovtr' not in x[0]:                
                    x[1]=''
                else:
                    videoinput2.append(x)
        elif sys.argv[1]=='s':
            for x in videoinput:
                if 'l' in x[0] and 'ovtr' not in x[0]:
                    x[1]=''
                else:
                    videoinput2.append(x)
    #videoinput=[('axis',f'!root:pass@192.168.10.132:10')]
    #videoinput=[('cam1','!root:pass@10.140.98.132:10'),('cam2','!root:pass@10.140.98.147:10'),('cam3','!root:pass@10.140.98.150:10')]
    workerpool = Pool(processes=len(videoinput2))
    workerpool.map(readFrametoShm, videoinput2)
    #readFrametoShm(videoinput[5])
    print("Workers launched")
