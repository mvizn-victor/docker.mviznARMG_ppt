#version:id22
##gi01
#processing disable bit
#processing 0 when waiting
##ha03
#  snapshot 0s and 5s after job
##id22
#  new paddleocr results[0] instead of result

def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

capturedphoto=0
import cv2
from memcachehelper import memcacheRW as mcrw
def addnumber(number):
    pmnumbers=mcrw.raw_read('pmnumbers',set())
    pmnumbers.add(number)
    mcrw.raw_write('pmnumbers',pmnumbers)

try:
    import os
    from paddleocr import PaddleOCR,draw_ocr
    import PIL
    import numpy as np
    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
    # to switch the language model in order.
    ocr = PaddleOCR(show_log=False,use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
    def nptoPIL(x):
        return PIL.Image.fromarray(x[:,:,::-1])
    def PILtonp(x):
        return np.array(x)[:,:,::-1]
    def ocr_and_draw(im_np):
        result=ocr.ocr(im_np)
        if 0: #OLDER VERSION
            boxes = [line[0] for line in result]
            txts = [line[1][0] for line in result]
            scores = [line[1][1] for line in result]
        boxes = [line[0] for line in result[0]]
        txts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]        
        im_annot = draw_ocr(im_np, boxes, txts, scores, font_path='fonts/simfang.ttf')
        return txts,im_annot
    if not os.path.exists('fonts/simfang.ttf'):
        raise
    usepaddleocr=True
    open('/tmp/usepaddleocr','w').write('1')
except:
    usepaddleocr=False 
    open('/tmp/usepaddleocr','w').write('0')

import re
import sys
from cabindetect import *

from datetime import datetime,timedelta
import numpy as np
import os
import glob
from config.config import * #import everything from Utils.helper too
from collections import defaultdict
import time
T=time.time()
plc=readplc()
SIDE=plc.SIDE
camraw = dict()
camnames= [f'ov{SIDE}s', f'pmn{SIDE}s']
for camname in camnames:
   camraw[camname] = sa.attach(f"shm://{camname}_raw")
#ha03
class C__DafterT0checker:
    def __init__(self,D):
        self.T0=0
        self.T1=0
        self.D=D
    def update(self):
        if self.T0==0:
            self.T0=time.time()
            return 0
        if self.T1==0 and time.time()-self.T0>=self.D:
            self.T1=time.time()
            return 1
        return 0
d__0s_checker={}
d__5s_checker={}
for camname in camnames:
    d__0s_checker[camname]=C__DafterT0checker(0)
    d__5s_checker[camname]=C__DafterT0checker(5)

lastJA=False
STATE='HOME'
pmnumber_match=0
lastpmnumber_read=''
mcrw.raw_write('pmnumber_match',pmnumber_match)
pmnrs_processing=0
mcrw.raw_write('pmnrs_processing',pmnrs_processing)
print(f'new job')
Tjobstart=mcrw.raw_read('Tjobstart',0)
assert Tjobstart!=0
pmnumber_match = 0
mcrw.raw_write('pmnumber_match', pmnumber_match)
cam_pmnumber_read = dict()
cam_lpnumber_read = dict()
plc = readplc()
SIDE = plc.SIDE
assert SIDE in 'ls'
pmnumber=plc.pmnumber
mcrw.raw_write('pmnrstop_active',time.time())
if 0:
    for (i,camname) in enumerate([f'ov{SIDE}s',f'pmn{SIDE}s']):
        cv2.namedWindow(camname)
        cv2.moveWindow(camname,i*960,0)



pmnrs_processing=time.time()
mcrw.raw_write('pmnrs_processing',pmnrs_processing)
ovxs=f'ov{SIDE}s'
pmnxs=f'pmn{SIDE}s'
camnames=[ovxs,pmnxs]

imshow=dict()
os.system('rm /dev/shm/*_pmnrstop')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_pmnrstop')
print('from textdetect import *')
from textdetect import *
#time.sleep(3)
#preload
print('from Utils.helper import dummyimage')
from Utils.helper import dummyimage
#print('gettextboxes(dummyimage)')
#gettextboxes(dummyimage)
#print('OCR(dummyimage)')
#OCR(dummyimage)

while True:
    #busy looping until gantry in place
    print('busy loop until gantry in place')
    mcrw.raw_write('pmnrstop_active',time.time())
    mcrw.raw_write('pmnrs_processing',0)
    plc=readplc()
    if abs(plc.GantryCurrSlot-plc.GantryTargetSlot)<=1:
        break
    time.sleep(0.5)
print('busy loop until gantry in place')
print('PMNRS STARTED')
Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
PHOTOLOGDIRNAME=f'/opt/captures/PMNRS/photologs/{JOBDATE}/{JOBTIME}'
PHOTOLOGRAWDIRNAME=f'/opt/captures/PMNRS/photologs_raw/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/PMNRS/logs/{JOBDATE}.txt'
frames=dict()
frames_raw=dict()
while True:
    T=time.time()
    #NOW = datetime.fromtimestamp(time.time()//10*10)
    NOW = datetime.fromtimestamp(time.time())
    DATE = NOW.strftime('%Y-%m-%d')
    TIME = NOW.strftime('%H-%M-%S.%f')    
    print(datetime.now(),"byte78",bin(plc.data[78])) 
    PMNRS_StopProcessing = plc.PMNRS_Enable #repurposed
    if PMNRS_StopProcessing:
        mcrw.raw_write('pmnrs_processing',0)
        mcrw.raw_write('pmnrstop_active',time.time())
        time.sleep(0.25)
        continue
    else:
        mcrw.raw_write('pmnrs_processing',time.time())
    
    for camname in [ovxs,pmnxs]:
        mcrw.raw_write('pmnrstop_active',time.time())
        mcrw.raw_write('pmnrs_processing',time.time())
        cam_pmnumber_read[camname]=''
        cam_lpnumber_read[camname]=''
        curr_pmnumber_read=''
        curr_lpnumber_read=''
        frame=camraw[camname].copy()
        frames_raw[camname]=frame
        frame_cpy=frame.copy()
        frames[camname]=frame_cpy

        if camname==ovxs:
            if time.time()-mcrw.raw_read(f'{camname}_ptz', 0)>1e6:
                #not using ovxs camera to detect if not ptz active
                continue
        
        #if camname==pmnxs:continue
        cabins, cabin_cropped, (x0, y0) = detectCabins_procimage(frame, camname)
        if usepaddleocr:
            if cabin_cropped is not None and cabin_cropped.shape[0] > 0 and cabin_cropped.shape[1]>0:
                txts,im_annot=ocr_and_draw(cabin_cropped)
                assignscaleimage(frames[camname],im_annot)
                txts=set(x.replace(' ','') for x in txts)
                pmnumbers=[]
                numbersdetected=[]
                nonnumbersdetected=[]
                nonnumberdetected=0
                for text in txts:
                    text=text.upper()
                    if not re.match('^[0-9A-Z]+$',text):continue
                    if not re.match('^[0-9]+$', text):
                        nonnumberdetected = 1
                    if 'IP' in text:
                        IPM = 1                        
                        match = re.match('^.*IP([0-9]{3,4}).*$', text)
                        if match is None:
                            match = re.match('^.*IPM([0-9]{3,4}).*$', text)
                        if match is not None:
                            text=match.groups()[0]
                        else:
                            text=''
                    else:
                        IPM = 0
                    # FIX PROBLEMATIC IPM NUMBERS

                    if not 3 <= len(text) <= 8: continue
                    if text == '': continue
                    if not re.match('^[0-9]+$', text):
                        nonnumbersdetected.append(text)
                    elif len(text) in [3, 4]:
                        numbersdetected.append(text)
                    else:
                        continue

                    if text == pmnumber:
                        text = pmnumber
                    elif pmnumber[1:3]=='PM':
                        if pmnumber[:3]+text==pmnumber:
                            text = pmnumber
                    elif IPM:
                        text = 'IPM' + text
                    pmnumbers.append(text)
                    if pmnumbers[-1] == pmnumber:
                        curr_pmnumber_read = pmnumber


                if curr_pmnumber_read == '':  # not match yet figure out what is the best number to send
                    if len(numbersdetected) > 0:
                        if not plc.ppm:
                            # assume IPM
                            curr_pmnumber_read = 'IPM' + numbersdetected[0]
                        else:
                            # assume PPM
                            #curr_pmnumber_read = 'PPM' + numbersdetected[0]
                            # KPM BPM PPM
                            curr_pmnumber_read = pmnumber[:3] + numbersdetected[0]
                    elif not plc.ppm:
                        pmnumbers.sort(key=len)
                        if len(pmnumbers) == 0:
                            curr_pmnumber_read = ''
                        elif len(pmnumbers) > 0:
                            # longest one
                            curr_pmnumber_read = pmnumbers[-1]
                nonnumbersdetected.sort(key=len)
                if len(nonnumbersdetected) == 0:
                    curr_lpnumber_read = ''
                else:
                    if not plc.ppm: 
                        curr_lpnumber_read = nonnumbersdetected[-1]
                cam_pmnumber_read[camname] = curr_pmnumber_read
                cam_lpnumber_read[camname] = curr_lpnumber_read
        else:           
            drawCabinBoxes_cabins(frame_cpy, cabins)
            
            if cabin_cropped is not None and cabin_cropped.shape[0] > 0 and cabin_cropped.shape[1] > 0:
                cropped_txts = sorted(gettextboxes(cabin_cropped))
                #cropped_txts=[cropped_txts[0],cropped_txts[2]]
                #stitch textboxes if overlap or near
                change=True
                #print(os.path.basename(imgfile))
                print('before:',cropped_txts)

                def stitchboxes(boxes0):
                    #boxes0=cropped_txts
                    boxes=sorted(boxes0)
                    boxes=[(x1,y1,x2,y2) for (x1,y1,x2,y2) in boxes if y2-y1!=0 and x2-x1!=0]
                    links=[]
                    deleted=set()    
                    for i1,b1 in enumerate(boxes):
                        for i2,b2 in enumerate(boxes):
                            if i2<=i1:continue
                            b1,b2=sorted([b1,b2])
                            x11,y11,x12,y12=b1
                            x21,y21,x22,y22=b2
                            w1=x12-x11
                            h1=y12-y11
                            w2=x22-x21
                            h2=y22-y21
                            w=min(w1,w2)
                            h=min(h1,h2)
                            #print(abs(y11 - y21) / h , abs(y12 - y22) / h , (x12 + h, x21), (x22 + h , x11))
                            cancombine=abs(y11-y21)/h<=0.4 and abs(y12-y22)/h<=0.4 and (x12+h>=x21)
                            if cancombine:
                                links.append((b1,b2))
                                break    
                    while len(links)>0:        
                        b1,b2=links.pop()
                        deleted.add(b1)
                        deleted.add(b2)
                        print('b1:',b1,'b2:',b2,'deleted:',sorted(deleted))
                        x11,y11,x12,y12=b1
                        x21,y21,x22,y22=b2
                        w1=x12-x11
                        h1=y12-y11
                        w2=x22-x21
                        h2=y22-y21        
                        w=min(w1,w2)
                        h=min(h1,h2)
                        b3=(min(x11,x21),min(y11,y21),max(x12,x22),max(y12,y22))        
                        print('b3:',b3)
                        if b3 in deleted:
                            deleted.remove(b3)
                        boxes.append(b3)
                        if 0:
                            im=np.zeros((400,400,3),dtype=np.uint8)
                            for box in boxes:
                                if box not in deleted:
                                    cv2.rectangle(im,box[:2],box[2:],(255,255,255))
                            for box in [b1,b2]:
                                cv2.rectangle(im,box[:2],box[2:],(0,255,255))
                            for box in [b3]:
                                cv2.rectangle(im,box[:2],box[2:],(0,255,0))
                            imshow(im)
                            time.sleep(0.2)
                        newlinks=[]
                        for link in links:
                            if link[1]==b1 or link[1]==b2:
                                if link[0]!=b3:
                                    newlinks.append((link[0],b3))
                            elif link[0]==b1 or link[0]==b2:
                                if link[1]!=b3:
                                    newlinks.append((b3,link[1]))
                            else:
                                newlinks.append(link)
                        links=newlinks
                    outboxes=[]
                    for box in set(boxes):
                        if box not in deleted:
                            outboxes.append(box)
                    return outboxes
                                                        
                cropped_txts = stitchboxes(cropped_txts)
                print('after:',cropped_txts)
                pmnumbers=[]
                numbersdetected=[]
                nonnumbersdetected=[]
                nonnumberdetected=0
                #bm3
                for x1, y1, x2, y2 in cropped_txts:
                    textprobs=[]
                    for inverted in [1,0]:
                        image=cabin_cropped[y1:y2,x1:x2]
                        if inverted:
                            image=image[::-1,::-1]
                        text,prob=OCR(image)
                        textprobs.append([text,prob,text])
                        if not re.match('^[0-9]+$', text):
                            nonnumberdetected = 1
                        if 'IP' in text:
                            IPM = 1                        
                            match = re.match('^.*IP([0-9]{3}).*$', text)
                            if match is None:
                                match = re.match('^.*IPM([0-9]{3}).*$', text)
                            if match is not None:
                                text=match.groups()[0]
                            else:
                                text=''
                        else:
                            IPM = 0
                        # FIX PROBLEMATIC IPM NUMBERS

                        if not 3 <= len(text) <= 8: continue
                        if text == '': continue
                        if not re.match('^[0-9]+$', text):
                            nonnumbersdetected.append(text)
                        elif len(text) in [3, 4]:
                            numbersdetected.append(text)
                        else:
                            continue
                        def inverttext(text):
                            DICT={'0':'0','1':'1','5':'5','6':'9','8':'8','9':'6'}
                            try:
                                return ''.join(DICT[c] for c in reversed(text))
                            except:
                                return ''
                        invertedtext=inverttext(text)                        
                        if text == pmnumber:
                            text = pmnumber
                            textprobs[-1][1]=2
                        elif pmnumber[1:3]=='PM':
                            if pmnumber[:3]+text==pmnumber or pmnumber[:3]+invertedtext==pmnumber:
                                text = pmnumber
                            textprobs[-1][1]=2
                        elif IPM:
                            text = 'IPM' + text
                            textprobs[-1][1]=1.5
                        textprobs[-1][2] = text
                    textorigmaxprob=max(textprobs,key=lambda x:x[1])[0]
                    textmaxprob=max(textprobs,key=lambda x:x[1])[2]
                    drawtext(x1, y1, x2, y2, frame_cpy, x0, y0,textorigmaxprob)
                    pmnumbers.append(textmaxprob)
                    if textmaxprob == pmnumber:
                        curr_pmnumber_read = pmnumber

                if curr_pmnumber_read == '':  # not match yet figure out what is the best number to send
                    if len(numbersdetected) > 0:
                        if not plc.ppm:
                            # assume IPM
                            curr_pmnumber_read = 'IPM' + numbersdetected[0]
                        else:
                            # assume PPM
                            #curr_pmnumber_read = 'PPM' + numbersdetected[0]
                            # KPM BPM PPM
                            curr_pmnumber_read = pmnumber[:3] + numbersdetected[0]
                    elif not plc.ppm:
                        pmnumbers.sort(key=len)
                        if len(pmnumbers) == 0:
                            curr_pmnumber_read = ''
                        elif len(pmnumbers) > 0:
                            # longest one
                            curr_pmnumber_read = pmnumbers[-1]
                # figure out what lpnumber to send
                nonnumbersdetected.sort(key=len)
                if len(nonnumbersdetected) == 0:
                    curr_lpnumber_read = ''
                else:
                    if not plc.ppm: 
                        curr_lpnumber_read = nonnumbersdetected[-1]
                cam_pmnumber_read[camname] = curr_pmnumber_read
                cam_lpnumber_read[camname] = curr_lpnumber_read
                
    for camname in [ovxs,pmnxs]:
        assignimage(imshow[camname],frames[camname])
    if pmnumber in cam_pmnumber_read.values():
        #matches
        pmnumber_read=pmnumber
    elif cam_pmnumber_read[pmnxs]!='':
        #favour PMNXS
        pmnumber_read=cam_pmnumber_read[pmnxs]
    else:
        pmnumber_read=cam_pmnumber_read[ovxs]

    if pmnumber in cam_lpnumber_read.values():
        #matches
        lpnumber_read=pmnumber
    elif cam_lpnumber_read[pmnxs]!='':
        #favour PMNXS
        lpnumber_read=cam_lpnumber_read[pmnxs]
    else:
        lpnumber_read=cam_lpnumber_read[ovxs]
    
    #when crane reach position take a snapshot
    if abs(plc.GantryTargetSlot-plc.GantryCurrSlot)==0 and abs(plc.GantryTargPosMM-plc.GantryCurrPosMM)<=100 and not capturedphoto:
        capturedphoto=1
        for camname in [ovxs,pmnxs]:
            makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}.jpg',frames[camname])
            makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}.jpg',frames_raw[camname])

    #ha03
    inposition=abs(plc.GantryTargetSlot-plc.GantryCurrSlot)==0 and abs(plc.GantryTargPosMM-plc.GantryCurrPosMM)<=100
    print(camname,'inposition',inposition,plc.GantryTargPosMM,plc.GantryCurrPosMM)
    if inposition:
        if d__0s_checker[camname].T0==0:
            print(camname,'set checker T0')
        for camname in camnames:
            snapshotcond_0s=d__0s_checker[camname].update()
            snapshotcond_5s=d__5s_checker[camname].update()
            frame_cpy=frames[camname]
            frame=frames_raw[camname]
            if snapshotcond_0s:
                print(camname,'snapshot 0s',1)
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot_0s/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot_0s/{DATE}_{TIME}_{camname}.jpg', frame)
            if snapshotcond_5s:
                print(camname,'snapshot 5s',1)
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot_5s/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot_5s/{DATE}_{TIME}_{camname}.jpg', frame)

    if pmnumber_read!=lastpmnumber_read and pmnumber_read!='':
        printandlog(f'{JOBDATE}_{JOBTIME}',f'{DATE}_{TIME}',cam_pmnumber_read[ovxs],cam_pmnumber_read[pmnxs],cam_lpnumber_read[ovxs],cam_lpnumber_read[pmnxs],file=makedirsopen(LOGFILENAME,'a'),sep=",")
        for camname in [ovxs,pmnxs]:
            if cam_pmnumber_read[camname]!='':
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}.jpg',frames[camname])
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}.jpg',frames_raw[camname])

    lastpmnumber_read=pmnumber_read
    if pmnumber_read==pmnumber and pmnumber!='':
        pmnumber_match=1
        mcrw.raw_write('pmnumber_match',time.time())
    #if not ppm continue detecting license plate for additional 5 seconds after pmnumber match (not implemented)

    mcrw.raw_write('pmnumber_read',pmnumber_read)
    mcrw.raw_write('lpnumber_read',lpnumber_read)
    addnumber(pmnumber_read)
    addnumber(lpnumber_read)
    if pmnumber_match:
        for camname in camnames:
            #snapshot if not yet cos already matched, for completeness
            snapshotcond_0s=d__0s_checker[camname].T1==0
            snapshotcond_5s=d__5s_checker[camname].T1==0
            frame_cpy=frames[camname]
            frame=frames_raw[camname]
            if snapshotcond_0s:
                print(camname,'snapshot 0s',2)
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot_0s/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot_0s/{DATE}_{TIME}_{camname}.jpg', frame)
            if snapshotcond_5s:
                print(camname,'snapshot 5s',2)
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot_5s/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
                makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot_5s/{DATE}_{TIME}_{camname}.jpg', frame)
        break
        
    Telapse=time.time()-T
    print(Telapse)
    time.sleep(max(0.5-Telapse,0))
time.sleep(3)

