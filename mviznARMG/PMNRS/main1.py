
import cv2
from memcachehelper import memcacheRW as mcrw
import SharedArray as sa



import re
import sys
from cabindetect import *
from textdetect import *
from datetime import datetime,timedelta
import numpy as np
import os
import glob
from config.config import * #import everything from Utils.helper too
from collections import defaultdict

camraw=dict()
for camname in ['ovls','ovss','pmnls','pmnss']:
    camraw[camname]=sa.attach(f"shm://{camname}_raw")

lastJA=False
STATE='HOME'
pmnumber_match=0
lastpmnumber_read=''
mcrw.raw_write('pmnumber_match',pmnumber_match)
pmnrs_processing=0
mcrw.raw_write('pmnrs_processing',pmnrs_processing)

      
while True:
    mcrw.raw_write('pmnumber_lastT',time.time())
    plc=readplc()
    SIDE=plc.SIDE
    if lastJA and not plc.JA:
        #job end
        pmnumber_match=0
        mcrw.raw_write('pmnumber_match',pmnumber_match)
        pmnrs_processing=0
        mcrw.raw_write('pmnrs_processing',pmnrs_processing)
        print(f'job ended: {STATE}->HOME')
        STATE='HOME'
        cv2.destroyAllWindows()
    if not lastJA and plc.JA:
        lastpmnumber_read=''
        cam_pmnumber_read=dict()
    
    if STATE=='HOME' and plc.JA and not pmnumber_match and SIDE in 'ls':
        for (i,camname) in enumerate([f'ov{SIDE}s',f'pmn{SIDE}s']):
            cv2.namedWindow(camname)
            cv2.moveWindow(camname,i*960,0)
        pmnumber=plc.pmnumber        
        print(f'job started: {STATE}->DETECT')
        STATE='DETECT'

    if STATE=='DETECT' and SIDE in 'ls':
        pmnrs_processing=1
        mcrw.raw_write('pmnrs_processing',pmnrs_processing)
        ovxs=f'ov{SIDE}s'
        pmnxs=f'pmn{SIDE}s'
        frames=dict()
        for camname in [ovxs,pmnxs]:
            frame=camraw[camname]
            frame_cpy=frame.copy()
            frames[camname]=frame_cpy
            cam_pmnumber_read[camname]=''
            curr_pmnumber_read=''            
            results, cabin_cropped, (x0, y0) = detectCabins(frame)
            drawCabinBoxes(frame_cpy, results)
            if cabin_cropped is not None and cabin_cropped.shape[0] > 0 and cabin_cropped.shape[1] > 0:
                cropped_txts = sorted(gettextboxes(cabin_cropped))
                #cropped_txts=[cropped_txts[0],cropped_txts[2]]
                #stitch textboxes if overlap or near
                change=True
                #print(os.path.basename(imgfile))
                print(cropped_txts)
                while change:
                    change=False
                    new_cropped_txts=[]
                    toremove=[]
                    for i1,b1 in enumerate(cropped_txts):
                        if not change:
                            for i2,b2 in enumerate(cropped_txts):
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
                                cancombine=abs(y11-y21)/h<=0.2 and abs(y12-y22)/h<=0.2 and (x12+h>=x21)
                                if cancombine:
                                    print('can combine:',b1,b2)
                                    toremove=[b1,b2]
                                    b1=(min(x11,x21),min(y11,y21),max(x12,x22),max(y12,y22))
                                    print('replaced by:',b1)
                                    change=True
                                    break
                        if b1 not in toremove:
                            new_cropped_txts.append(b1)
                    cropped_txts=new_cropped_txts
                print(cropped_txts)
                pmnumbers=[]
                numbersdetected=[]
                nonnumberdetected=0
                for x1, y1, x2, y2 in cropped_txts:
                    text = doOCR(cabin_cropped, [[x1, y1, x2, y2]], frame_cpy, x0, y0)
                    if not 3<=len(text)<=8:continue
                    if text=='':continue
                    if not re.match('[0-9]*',text):
                        nonnumberdetected=1
                    elif len(text) in [3,4]:
                        numbersdetected.append(text)
                    if text.startswith('IP'):
                        text=text.replace('IP','IPM')                                              
                    if 'IPM'+text==pmnumber:
                        text=pmnumber
                    if 'PPM'+text==pmnumber:
                        text=pmnumber
                                                
                    pmnumbers.append(text)         
                    if text==pmnumber:
                        curr_pmnumber_read=pmnumber
                                            
                if curr_pmnumber_read=='': #not match yet figure out what is the best number to send
                    if len(numbersdetected)>0:
                        if nonnumberdetected:
                            #assume IPM
                            curr_pmnumber_read='IPM'+numbersdetected[0]
                        else:
                            #assume PPM
                            curr_pmnumber_read='PPM'+numbersdetected[0]
                    else:
                        pmnumbers.sort(key=len)
                        if len(pmnumbers)==0:
                            curr_pmnumber_read=''
                        elif len(pmnumbers)>0:
                            curr_pmnumber_read=pmnumbers[-1]
                cam_pmnumber_read[camname]=curr_pmnumber_read
        for camname in [ovxs,pmnxs]:                
            cv2.imshow(camname, cv2.resize(frames[camname],(960,540)))
            c=cv2.waitKey(1)
        if pmnumber in cam_pmnumber_read.values():
            #matches
            pmnumber_read=pmnumber
        elif cam_pmnumber_read[pmnxs]!='':
            #favour PMNXS
            pmnumber_read=cam_pmnumber_read[pmnxs]
        else:
            pmnumber_read=cam_pmnumber_read[ovxs]
        if pmnumber_read!=lastpmnumber_read and pmnumber_read!='':
            print("HERE")
            NOW=datetime.now()
            DATE=NOW.strftime('%Y-%m-%d')
            TIME=NOW.strftime('%H-%M-%S')
            print(SIDE,datetime.strftime(NOW,f'{DATE}_{TIME}'),cam_pmnumber_read[ovxs],cam_pmnumber_read[pmnxs])
            os.makedirs(f'/opt/captures/PMNRS/{DATE}',exist_ok=True)
            for camname in [ovxs,pmnxs]:
                cv2.imwrite(f'/opt/captures/PMNRS/{DATE}/{TIME}_{camname}.jpg',frames[camname])
                #print(len(cropped_txts))
                #cv2.imshow("Cabin", cabin_cropped_cpy)
                        
        lastpmnumber_read=pmnumber_read
        if pmnumber_read==pmnumber and pmnumber!='':
            pmnumber_match=1
            mcrw.raw_write('pmnumber_match',pmnumber_match)
            pmnrs_processing=0
            mcrw.raw_write('pmnrs_processing',pmnrs_processing)            
            print(f'MATCH: {STATE}->HOME, Read:{pmnumber_read}')
            STATE='HOME'
        mcrw.raw_write('pmnumber_read',pmnumber_read)
        
        
