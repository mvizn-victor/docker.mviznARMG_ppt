import sys
from cabindetect import *
from textdetect import *
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
videop3 = '/mnt/NFSDIR/YardVideos_converted/20190701/PMNLS/7110_PMNLS_20190606_210000.mp4'
import os
import glob
import cv2
import time
import numpy as np
detectCabins(np.zeros((3,3,3),dtype=np.uint8))
cap=cv2.VideoCapture(videop3)
i=0
while 1:
    T=time.time()
    ret,frame=cap.read()
    i+=1
    if i<=31*60*25:continue
    if not ret:
        break
    frame_cpy=frame.copy()
    results, cabin_cropped, (x0, y0) = detectCabins(frame)
    #cv2.imwrite('image.jpg', cabin_cropped)
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
            for x1, y1, x2, y2 in cropped_txts:
                textprobs=[]
                for inverted in [1,0]:
                    image=cabin_cropped[y1:y2,x1:x2]
                    if inverted:
                        image=image[::-1,::-1]
                    text,prob=OCR(image)
                    textprobs.append([text,prob])
                textorig=max(textprobs,key=lambda x:x[1])[0]
                drawtext(x1, y1, x2, y2, frame_cpy, x0, y0,textorig)
                                
    cv2.imshow('',frame_cpy)
    c=cv2.waitKey(1)
    if c==ord('1'):
        for _ in range(10-1):
            ret,frame=cap.read()
            i+=1
    if c == ord('2'):
        for _ in range(20 - 1):
            ret, frame = cap.read()
            i+=1
    if c == ord('3'):
        for _ in range(50 - 1):
            ret, frame = cap.read()
            i+=1
    print(i)
