#version:gd21
#fk14-atpostxt return False if fail
#gd21-atpostxt wrap
#gh16-plc.data#
import sys
import os
import SharedArray as sa
import requests
from requests.auth import HTTPDigestAuth
from threading import Thread
from PIL import Image
import PIL.ExifTags
import io
import numpy as np
import cv2
import json
import pickle
from memcachehelper import memcacheRW as mcrw
import struct
simulation=os.path.exists('/dev/shm/simARMG')
if simulation:
    from datetime import timedelta
    from datetime import datetime as origdatetime
    import time as origtime
    class time:
        sleep=origtime.sleep
        def time():
            while 1:
                try:
                    return float(open('/dev/shm/sim_timestamp').read())
                except:
                    pass
    class datetime(origdatetime):
        def now():
            return origdatetime.fromtimestamp(time.time())
else:
    from datetime import datetime,timedelta
    import time
b=[1]
for i in range(1,8):
    b.append(b[i-1]<<1)
dummyimage=np.zeros([3,3,3],dtype=np.uint8)
class PLC:
    lastHoistPos=0
    lastT=0
    speed=0
    def __init__(self, DataR, T):
        if os.path.exists('/tmp/plc.dat'):
            unpacker = struct.Struct('!1i 1h 4c'
             '4i'
             '3h'
             '2i'
             '3h'
             '2i'
             '2h'
             '4h'
             '7h')
            self.fake=1
            DataR = list(unpacker.unpack(open('/tmp/plc.dat','rb').read()))
        else:
            self.fake=0

        self.DataR = DataR
        self.JA = DataR[2][0]&b[1]>0 #job active            
        self.TLOCK = DataR[2][0]&b[3]>0 #twistlock
        self.MI = DataR[5][0]&b[0]>0 #MI
        self.CNRSCompleted = DataR[4][0]&b[6]>0 or DataR[4][0]&b[7]>0 #CNRSCompleted or PMMS Completed
        self.LAND = DataR[2][0]&b[7]>0
        if DataR[3][0]&b[7]>0:
            self.JOBTYPE='OFFLOADING'
        elif DataR[3][0]&b[6]>0:
            self.JOBTYPE='MOUNTING'        
        else:
            self.JOBTYPE = 'OTHERS'

            
        self.HoistPos = DataR[18]
        if T!=PLC.lastT:
            PLC.speed = self.HoistPos - PLC.lastHoistPos
            if PLC.lastT==0:PLC.speed=0
            PLC.lastHoistPos=self.HoistPos
            PLC.lastT=T

            
        self.TrolleyPos = DataR[15]
        self.SIDEINFO = DataR[15] #currentrow during simulation    
        if self.JOBTYPE=='MOUNTING':
            self.SIDEINFO = DataR[17]
        elif self.JOBTYPE=='OFFLOADING':
            self.SIDEINFO = DataR[16]

        self.GantryCurrSlot=DataR[10]
        self.GantrySrcSlot=DataR[11]
        self.GantryDestSlot=DataR[12]
        self.GantryTargetSlot=-99
        if self.JOBTYPE=='MOUNTING':
            self.GantryTargetSlot=self.GantryDestSlot
        elif self.JOBTYPE=='OFFLOADING':
            self.GantryTargetSlot=self.GantrySrcSlot

        if self.SIDEINFO == 0:
            self.SIDE = 's'
        elif self.SIDEINFO == 11:
            self.SIDE = 'l'
        else:
            self.SIDE = 'x'
        self.containerpos = 0
        for i in range(0, 6):
            if DataR[4][0]&b[i]>0:
                self.containerpos = i + 1
                break
        self.size = 0            
        if DataR[2][0]&b[4]>0:
            self.size = 20
        elif DataR[2][0]&b[5]>0:
            self.size = 40
        elif DataR[2][0]&b[6]>0:
            self.size = 45
        
        #self.externalpm = DataR[3][4] == '1'
        self.pmnumber4int=str(DataR[22:26])
        try:
            self.pmnumber=b''.join(list(x.to_bytes(2,'big') for x in DataR[22:26])).decode('utf8').replace('\x00','').replace(' ','')
        except:
            self.pmnumber='ERROR'            
        self.contnum6int=str(DataR[26:32])
        try:
            self.contnum=b''.join(list(x.to_bytes(2,'big') for x in DataR[26:32])).decode('utf8').replace('\x00','').strip()
            if len(self.contnum)==11:
                self.contnum=self.contnum[:4]+' '+self.contnum[-7:]
            elif len(self.contnum)==7:
                self.contnum=' '*5+self.contnum
        except:
            self.contnum='ERROR'
        #self.externalpm = self.pmnumber[:3]!='PPM'
        self.ppm = self.pmnumber[1:3] == 'PM' and self.pmnumber[:1]!='I'
        self.externalpm = not self.ppm
        self.dst = DataR[3][0]&b[3]>0
        self.craneon = DataR[5][0] & b[1] > 0
        self.HNCDS_Validity = DataR[32] & b[0] > 0
        self.TCDS_Validity = DataR[32] & b[1] > 0
        self.PMNRS_Validity = DataR[32] & b[2] > 0
        self.CLPS_Validity = DataR[32] & b[3] > 0
        self.HNCDS_Enable = DataR[32] & b[4] > 0
        self.TCDS_Enable = DataR[32] & b[5] > 0
        self.PMNRS_Enable = DataR[32] & b[6] > 0
        self.CLPS_Enable = DataR[32] & b[7] > 0
        #self.print()
        
       
    def getEstHoistPos(self):
        return self.HoistPos+(time.time()-self.lastT)/0.5*self.speed
    def print(self):
        #for attr in sorted(dir(self)):
        keyattrs=['JA','MI','CNRSCompleted','JOBTYPE','TLOCK','LAND']
        for attr in keyattrs:
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")        
        for attr in sorted(dir(self)):
            if attr in keyattrs:continue
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")
        print()
class PLC2:
    lastHoistPos=0
    lastT=0
    speed=0
    def __init__(self, data, T):
        if os.path.exists('/tmp/plc.dat'):
            data=open('/tmp/plc.dat','rb').read()
            self.data=data
            self.fake=1
        else:
            self.fake=0
        self.data=data
        self.JA = data[6]&b[1]>0 #job active            
        self.TLOCK = data[6]&b[3]>0 #twistlock
        self.MI = data[9]&b[0]>0 #MI
        self.CNRSCompleted = data[8]&b[6]>0 or data[8]&b[7]>0 #CNRSCompleted or PMMS Completed
        self.LAND = data[6]&b[7]>0
        if data[7]&b[7]>0:
            self.JOBTYPE='OFFLOADING'
        elif data[7]&b[6]>0:
            self.JOBTYPE='MOUNTING'        
        else:
            self.JOBTYPE = 'OTHERS'

            
        self.HoistPos = struct.unpack('>i',data[46:50])[0]
        if T!=PLC2.lastT:
            PLC2.speed = self.HoistPos - PLC2.lastHoistPos
            if PLC2.lastT==0:PLC2.speed=0
            PLC2.lastHoistPos=self.HoistPos
            PLC2.lastT=T

        self.TrolleyPosCurrMM = struct.unpack('>l',data[32:36])[0]
        self.TrolleyPosTargMM = struct.unpack('>l',data[36:40])[0]
        self.TrolleyPosSrc = struct.unpack('>h',data[42:44])[0]
        self.TrolleyPosDest = struct.unpack('>h',data[44:46])[0]
        self.TrolleyPos = struct.unpack('>h',data[40:42])[0]
        self.SIDEINFO = self.TrolleyPos #currentrow during simulation    
        if self.JOBTYPE=='MOUNTING':
            self.SIDEINFO = struct.unpack('>h',data[44:46])[0]
        elif self.JOBTYPE=='OFFLOADING':
            self.SIDEINFO = struct.unpack('>h',data[42:44])[0]

        self.GantryCurrSlot=struct.unpack('>h',data[26:28])[0]
        self.GantrySrcSlot=struct.unpack('>h',data[28:30])[0]
        self.GantryDestSlot=struct.unpack('>h',data[30:32])[0]
        self.GantryCurrPosMM=struct.unpack('>i',data[10:14])[0]
        self.GantryTargPosMM=struct.unpack('>i',data[14:18])[0]
        self.GantryTargetSlot=-99
        if self.JOBTYPE=='MOUNTING':
            self.GantryTargetSlot=self.GantryDestSlot
        elif self.JOBTYPE=='OFFLOADING':
            self.GantryTargetSlot=self.GantrySrcSlot

        if self.SIDEINFO == 0:
            self.SIDE = 's'
        elif self.SIDEINFO == 11:
            self.SIDE = 'l'
        else:
            self.SIDE = 'x'
        self.containerpos = 0
        for i in range(0, 6):
            if data[8]&b[i]>0:
                self.containerpos = i + 1
                break
        self.size = 0            
        if data[6]&b[4]>0:
            self.size = 20
        elif data[6]&b[5]>0:
            self.size = 40
        elif data[6]&b[6]>0:
            self.size = 45
        
        try:
            self.pmnumber=data[58:66].replace(b'\x00',b'').decode('utf8').strip()
        except:
            self.pmnumber='ERROR'
        try:
            self.contnum=data[66:78].replace(b'\x00',b'').decode('utf8').strip()
            if len(self.contnum)==11:
                self.contnum=self.contnum[:4]+' '+self.contnum[-7:]
            elif len(self.contnum)==7:
                self.contnum=' '*5+self.contnum
        except:
            self.contnum='ERROR'
        self.externalpm = self.pmnumber[:3]!='PPM'
        self.ppm = self.pmnumber[:3] == 'PPM'
        self.dst = data[7] & b[3] > 0
        self.craneon = data[9] & b[1] > 0
        self.HNCDS_Validity = data[78] & b[0] > 0
        self.TCDS_Validity = data[78] & b[1] > 0
        self.PMNRS_Validity = data[78] & b[2] > 0
        self.CLPS_Validity = data[78] & b[3] > 0
        self.HNCDS_Enable = data[78] & b[4] > 0
        self.TCDS_Enable = data[78] & b[5] > 0
        self.PMNRS_Enable = data[78] & b[6] > 0
        self.CLPS_Enable = data[78] & b[7] > 0
        self.HNCDS_OpsAck = data[79] & b[0] > 0
        self.PMNRS_NoOpsAck = data[79] & b[1] > 0
        self.TCDS_OpsAck = data[79] & b[2] > 0
        self.CLPS_OpsAck = data[79] & b[3] > 0
        #self.print()
        self.heartbeat_echo = struct.unpack('>B',data[80:81])[0]

       
    def getEstHoistPos(self):
        return self.HoistPos+(time.time()-self.lastT)/0.5*self.speed
    def print(self):
        #for attr in sorted(dir(self)):
        keyattrs=['JA','MI','CNRSCompleted','JOBTYPE','TLOCK','LAND']
        for attr in keyattrs:
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr=='data' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")        
        for attr in sorted(dir(self)):
            if attr in keyattrs:continue
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr=='data' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")
        print()
        
class AxisCamera:
    def __init__(self, ip, uname, passwd):
        self.ip = ip
        self.auth = HTTPDigestAuth(uname, passwd)

    def ptz(self, args):
        return requests.get(f'http://{self.ip}/axis-cgi/com/ptz.cgi?{args}', auth=self.auth, timeout=1).content

    def setposition(self, pos):
        if 0:
            self.ptz(f'pan={pos["pan"]}')
            time.sleep(0.1)
            self.ptz(f'tilt={pos["tilt"]}')
            time.sleep(0.1)
            self.ptz(f'zoom={pos["zoom"]}')
        self.ptz(f'pan={pos["pan"]}&tilt={pos["tilt"]}&zoom={pos["zoom"]}')

    def position(self):
        s = self.ptz('query=position').decode('utf8')
        D = {}
        for line in s.split():
            k, v = line.split('=')
            if v in ['on', 'off']:
                # D[k]=(v=='on')
                D[k] = v
            else:
                try:
                    D[k] = int(v)
                except:
                    D[k] = float(v)
        return D

    def savepos(self, fname):
        open(fname, 'w').write(json.dumps(self.position()))

    def loadposthread(self, pos):
        if simulation:
            return True
        for i in range(3):
            try:
                self.setposition(pos)
                break
            except:                
                print('set position', 'error redo')
                time.sleep(0.05)

    def loadpos(self, fname):
        """load pos from json file"""
        if simulation:
            return True
        pos = json.loads(open(fname).read())
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()

    def loadpostxt(self, fname, tiltoffset=None, forcezoom=None):
        """load pos from text file"""
        if simulation:
            return True
        pos = dict()
        for line in open(fname).read().strip().split():
            k, v = line.split('=')
            pos[k] = v
        if tiltoffset is not None:
            pos['tilt']=float(pos['tilt'])+tiltoffset
        if forcezoom is not None:
            pos['zoom']=forcezoom
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()
    
    def atpostxt(self, fname, tiltoffset=None, forcezoom=None):
        """load pos from text file"""
        if simulation:
            return True
        pos = dict()
        for line in open(fname).read().strip().split():
            k, v = line.split('=')
            pos[k] = float(v)
        if tiltoffset is not None:
            pos['tilt']=float(pos['tilt'])+tiltoffset
        if forcezoom is not None:
            pos['zoom']=float(forcezoom)
        try:
            postarget=self.position()
            #gd21
            return min((postarget['pan']-pos['pan'])%360,(pos['pan']-postarget['pan'])%360)<=0.1 and abs(postarget['tilt']-pos['tilt'])<=0.1 and abs(postarget['zoom']-pos['zoom'])<=0.1
        except:
            return False
    def loadposstr(self, s):
        """load pos from string"""
        if simulation:
            return True
        pos = dict()
        for line in s.strip().split():
            k, v = line.split('=')
            pos[k] = v
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()

    def positiontxt(self):
        if simulation:
            return 'pan=0\ntilt=0\nzoom=0'
        s=(self.ptz('query=position').decode('utf8'))
        print(s)
        return(s)

    def snapshotthread(self, filename,delay):
        try:
            time.sleep(delay)
            image=requests.get(f'http://{self.ip}/axis-cgi/jpg/image.cgi?resolution=1280x720', auth=self.auth, timeout=1).content
            open(filename,'wb').write(image)
        except:
            pass

    def snapshot(self,filename,delay=0):
        DIR=os.path.dirname(filename)
        if DIR!='':
            os.makedirs(DIR,exist_ok=True)
        thread = Thread(target=self.snapshotthread, args=(filename,delay), daemon=True)
        thread.start()

    def snapshotimage(self):
        try:
            image=requests.get(f'http://{self.ip}/axis-cgi/jpg/image.cgi?resolution=1280x720', auth=self.auth, timeout=1).content
            return image
        except:
            return None
            pass
        
    def nonptzautofocusthread(self):
        return requests.get(f'http://{self.ip}/axis-cgi/opticssetup.cgi?autofocus=perform', auth=self.auth, timeout=20).content

    def nonptzautofocus(self):
        thread = Thread(target=self.nonptzautofocusthread, daemon=True)
        thread.start()

def readplc():
    if simulation:
        T, data = mcrw.raw_read('simARMGplcdata',[0,None])
        plc=PLC2(data,T)
        return plc
    while True:
        try:
            T, data = mcrw.raw_read('plcdata',[0,None])
            if os.path.exists('/tmp/plc.dat'):
                T=time.time()
            if time.time()-T>1:
                raise Exception(f'PLC stale by {time.time()-T}')
            break
        except Exception as e:
            print(e)
            pass
        time.sleep(0.5)
    plc = PLC2(data, T)
    return plc


def createShm(fbasename, shape=(720,1280,3), dtype=np.uint8):
    try:
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

def assignimage(x,img):
    if img.shape==x.shape:
        x[:] = img
    else:
        x[:] = cv2.resize(img, (x.shape[1],x.shape[0]))

def assignscaleimage(x,img):
    H,W=x.shape[:2]
    imgout=scaleimage(img,W,H)
    Hout,Wout=imgout.shape[:2]
    x[:]=0
    x[:Hout,:Wout]=imgout

def scaleimage(x,W,H):
    h,w=x.shape[:2]
    if w/h<W/H:
        wout=H*w//h
        hout=H
    else:
        wout=W
        hout=W*h//w
    if (wout,hout)==(w,h):
        return x
    else:
        #print(w,h,W,H,wout,hout)
        return cv2.resize(x,(wout,hout))

def makedirsopen(file,mode):
    DIR=os.path.dirname(file)
    if DIR!='':
        os.makedirs(DIR,exist_ok=True)
    return open(file,mode)

def makedirsimwrite(file,img):
    thread = Thread(target=_makedirsimwrite, args=(file,img), daemon=True)
    thread.start()

def _makedirsimwrite(file,img,overwrite=False):
    if not overwrite and os.path.exists(file):return
    DIR=os.path.dirname(file)
    if DIR!='':
        os.makedirs(DIR,exist_ok=True)
    return cv2.imwrite(file,img)

def printandlog(*x,file=None,sep=None):
    thread = Thread(target=_printandlog, args=x, kwargs={'file':file,'sep':sep}, daemon=True)
    thread.start()

def _printandlog(*x,file=None,sep=None):
    print(*x,sep=sep)
    print(*x,file=file,sep=sep)

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
            
def putText(frame,text,position,thickness=3,color=(255,0,0),font_scale=1,font = None,line_type = None):
    if font is None:font=cv2.FONT_HERSHEY_SIMPLEX
    if line_type is None:line_type=cv2.LINE_AA
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    line_height = (text_size[1] + 5)*6//5
    x, y0 = position
    for i, line in enumerate(text.split("\n")):
        y = y0 + i * line_height
        cv2.putText(frame,
                    line,
                    (x, y),
                    font,
                    font_scale,
                    color,
                    thickness,
                    line_type)
