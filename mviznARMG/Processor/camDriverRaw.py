#version:gc27
#gc19:
# use exif for newer camera firmware
#gc27
# bug fix
def print2(*x,**kw):
    from datetime import datetime
    #if 'file' not in kw:
    if 1:
        DT=datetime.now()
        x=(DT,)+x
    print(*x,**kw)
fslog="/dev/shm/fs.log"
import sys
import cv2
import requests
import numpy as np
from threading import Thread
from requests.auth import HTTPDigestAuth
CV_LOAD_IMAGE_COLOR = 1
import io
from PIL import Image
import PIL.ExifTags
import time
from datetime import datetime
from time import sleep
from memcachehelper import memcacheRW as mcrw
from collections import deque
import struct
class FrameGrabberRTSP(Thread):
    def __init__(self, divapath, nparray,camid):
        Thread.__init__(self, daemon=True, name=divapath)
        self.url = divapath
        self.camid=camid
        #self.uname = uname
        #self.passwd = passwd
        self.nparray = nparray
        self.interrupted = False
        #self.auth = HTTPDigestAuth(uname, passwd)
        #self.session = requests.session()

    def run(self):
        cap = cv2.VideoCapture(self.url)
        tqueue=deque([])
        while not self.interrupted:
            ret, frame = cap.read()
            #camT=cap.getRTPTimeStampSeconds()
            #camTfrac=cap.getRTPTimeStampFraction()
            #print(camT)
            if frame is not None:
                if frame.shape==self.nparray.shape:
                    self.nparray[:] = frame
                else:
                    self.nparray[:] = cv2.resize(frame, dsize=(self.nparray.shape[1], self.nparray.shape[0]))
                mcrw.raw_write(f'{self.camid}lastrawupdate', time.time())
                tqueue.append(time.time())
                if len(tqueue)==26:
                    print(self.camid,(len(tqueue)-1)/(tqueue[-1]-tqueue[0]))
                    tqueue.popleft()
            else:
                self.nparray[:]=0
            if 0:#self.camid=='cnlsbb':
                cv2.imshow(self.camid, self.nparray)
                cv2.waitKey(1)
            if self.interrupted:
                print(self.url + "... exiting")
                break
    def stop(self):
        self.interrupted = True




class FrameGrabber(Thread):
    def __init__(self, url, uname, passwd, nparray,camid):
        Thread.__init__(self, daemon=True, name=url)
        self.url = url
        self.camid=camid
        self.uname = uname
        self.passwd = passwd
        self.nparray = nparray
        self.interrupted = False
        self.auth = HTTPDigestAuth(uname, passwd)
        self.session = requests.session()
        
    def run(self):
        print2(self.camid,"start",file=open(fslog,"a"))
        while not self.interrupted:
            framebytes = bytes()
            HERE=0
            #datastream = requests.get(self.url, auth=(self.uname, self.passwd), stream=True)
            try:
                datastream = requests.get(self.url, auth=self.auth, stream=True, timeout=1)
                if datastream.status_code == 200:
                    print("Launched framgrabber from: " + self.url)
                    framenum=0
                    tqueue=deque([])
                    for chunk in datastream.iter_content(chunk_size=1024):
                        #print(self.url)
                        framebytes += chunk
                        t1=time.time()
                        a = framebytes.find(b'\xff\xd8')
                        b = framebytes.find(b'\xff\xd9')
                        tindex = framebytes.find(b'\xff\xfe\x00\x0f\x0a\x01')
                        t2=time.time()
                        
                        if a != -1 and b != -1:
                            HERE=1
                            start=time.time()
                            jpg = framebytes[a:b + 2]
                            if tindex != -1:
                                #print(binascii.hexlify(framebytes[tindex+6:tindex+11]))
                                unixtime_s, unixtime_hundredths = struct.unpack(">LB", framebytes[tindex+6:tindex+11])
                                Tjpgf = unixtime_s + unixtime_hundredths/100.0                            
                                print(self.camid,'tindex',time.time(),Tjpgf,time.time()-Tjpgf)
                                mcrw.raw_write(f'{self.camid}lastcamtime', Tjpgf)
                            HERE = 2
                            #print(framebytes[a+125:a+125+19])
                            img=Image.open(io.BytesIO(jpg))
                            HERE = 3
                            try:
                                if tindex!=-1:raise Exception('skip')
                                HERE='3a'
                                exif_data=(img._getexif())
                                HERE='3b'
                                exif = {
                                    PIL.ExifTags.TAGS[k]: v
                                    for k, v in img._getexif().items()
                                    if k in PIL.ExifTags.TAGS
                                }
                                HERE='3c'
                                Tjpg = exif['DateTimeDigitized']
                                HERE='3d'
                                Tjpgsubsec = int(exif['SubsecTimeDigitized'])
                                Tjpg=datetime.strptime(Tjpg+'.'+'%03d'%Tjpgsubsec,"%Y:%m:%d %H:%M:%S.%f")
                                #Tcomp=datetime.fromtimestamp(time.time())
                                HERE='3g'
                                Tjpgf2=Tjpg.timestamp()
                                if tindex==-1:
                                    Tjpgf=Tjpgf2
                                print(self.camid,'exif',time.time(),Tjpgf,time.time()-Tjpgf)
                                mcrw.raw_write(f'{self.camid}lastcamtime', Tjpgf)
                            except Exception as e:
                                if e.args[0]!='skip':
                                    print(self.camid,e,HERE)
                                pass
                            #print(Tcompf-Tjpgf)
                            framebytes = framebytes[b + 2:]
                            HERE=4
                            self.nparray[:] = np.array(img)[:,:,::-1]
                            HERE=5
                            mcrw.raw_write(f'{self.camid}lastrawupdate', time.time())
                            #cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), CV_LOAD_IMAGE_COLOR)
                            #cv2.imshow(self.camid, self.nparray)
                            #print(t1-Tjpgf, t2-t1, time.time()-start, time.time())
                            #cv2.waitKey(1)
                            tqueue.append(time.time())
                            if len(tqueue)==26:
                                print(self.camid,'fps',(len(tqueue)-1)/(tqueue[-1]-tqueue[0]))
                                tqueue.popleft()                        
                            framenum+=1
                            HERE=6
                        if self.interrupted:
                            print(self.url + "... exiting")
                            break
                        
                        
                else:
                    print(datastream.status_code)
                    print("Connection failed " + self.url)
            except Exception as e:
                print(e)
                print(self.camid,"HERE:",HERE)
                print2(e,file=open(fslog,"a"))
                print2(self.camid,"HERE:",HERE,file=open(fslog,"a"))
                pass
            self.nparray[:]=0
            print("sleeping", time.time())
            sleep(0.1)

    def stop(self):
        self.interrupted = True
