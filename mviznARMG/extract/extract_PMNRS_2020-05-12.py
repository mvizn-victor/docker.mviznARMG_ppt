import sys
from PMNRS.cabindetect import *
from PMNRS.textdetect import *
import SharedArray as sa
from datetime import datetime,timedelta
from memcachehelper import memcacheRW as mcrw
# PM
# 20ft Front
input_file_1 = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/20FT Front/OVLS 1905hrs.avi"

# 20ft Rear
input_file_2a = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/20FT Rear/OVLS 1909hrs.avi"
input_file_2b = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/20FT Rear/PMNLS 1909hrs.avi"

# 40ft
input_file_3a = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/40FT/OVLS 0920.avi"
input_file_3b = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/40FT/PMNLS 0920.avi"


# EH
# 20ft Front
input_file_4 = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/20FT Front/OVSS 1228.avi"

# 20ft Rear
input_file_5 = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/20FT Rear/OVSS 1241.avi"

# 40ft
input_file_6a = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/40FT/OVSS 1232.avi" # useless
input_file_6b = "/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/40FT/PMNSS 1232.avi"
videop1 = '/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/40FT/PMNSS 1232.avi'
videop2 = '/mnt/NFSDIR/Raw Videos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/PM/20FT Front/OVLS 1905hrs.avi'

import os
import glob
import cv2
import re
outd='/mnt/NFSDIR/ARMG-Project-Data/clps_pmnrs_retraining_out/pmnrs2'
os.makedirs(outd,exist_ok=True)
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

for f in open('/mnt/NFSDIR/ARMG-Project-Data/PMNRS/trainlist.txt'):
    f=f.strip()
    CRANE,DATE,BASE=re.match('/mnt/NFSDIR/ARMG-Project-Data/captures/(.*)/captures/PMNRS/photologs_raw/(.*)/.*/(.*).jpg',f).groups()
    cap=cv2.VideoCapture(f)
    framenum=0
    n=0
    while 1:
        ret,frame=cap.read()
        if not ret:break
        results, cabin_cropped, (x0, y0) = detectCabins(frame)
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
            if len(cropped_txts)>0:
                n+=1
            for boxi,(x1, y1, x2, y2) in enumerate(cropped_txts):
                #text = doOCR(cabin_cropped, [[x1, y1, x2, y2]], frame_cpy, x0, y0)
                fout=f'{outd}/{CRANE}_{DATE}_{BASE}_{framenum}_{boxi}.jpg'
                cv2.imwrite(fout,cabin_cropped[y1:y2,x1:x2])
        framenum+=1
        if n>=5:break



