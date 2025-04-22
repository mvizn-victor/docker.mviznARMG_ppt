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

import os
import glob
import cv2

while 1:
    #input_file='/home/mvizn/raid/rtg-train-uploads/93983159-d50d-43d4-9480-701da179341a/d7ccad7d-515e-4e2d-ad89-d6d5418c8531-53463b12-f549-43fb-9eff-21e0f04bd877/imgs/0_x.jpg'
    if len(sys.argv)<2:
        input_file='PMNRS/sample/1.jpg'
    else:
        input_file=sys.argv[1]
    frame=cv2.imread(input_file)
    #frame=cv2.rotate(frame,cv2.ROTATE_180)
    frame_cpy=frame.copy()
    cabins, cabin_cropped, (x0, y0) = detectCabins_procimage(frame,'ovls')
    #cv2.imwrite('image.jpg', cabin_cropped)
    drawCabinBoxes_cabins(frame_cpy, cabins)
    if cabin_cropped is not None and cabin_cropped.shape[0] > 0 and cabin_cropped.shape[1] > 0:
        cropped_txts = sorted(gettextboxes(cabin_cropped))
        #cropped_txts=[cropped_txts[0],cropped_txts[2]]
        #stitch textboxes if overlap or near
        change=True
        #print(os.path.basename(imgfile))
        print(cropped_txts)
        if 1:
            def stitchboxes(boxes0):
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
                    #print('b1:',b1,'b2:',b2,'deleted:',sorted(deleted))
                    if b1 in deleted or b2 in deleted:
                        #print('skip')
                        continue
                    deleted.add(b1)
                    deleted.add(b2)    
                    x11,y11,x12,y12=b1
                    x21,y21,x22,y22=b2
                    w1=x12-x11
                    h1=y12-y11
                    w2=x22-x21
                    h2=y22-y21        
                    w=min(w1,w2)
                    h=min(h1,h2)
                    b3=(min(x11,x21),min(y11,y21),max(x12,x22),max(y12,y22))
                    #print('b3:',b3)
                    boxes.append(b3)    
                    for link in links:
                        if link[1]==b1:
                            links.append((link[0],b3))
                        if link[0]==b2:
                            links.append((b3,link[1]))
                            break    
                outboxes=[]
                for box in boxes:        
                    if box not in deleted:
                        outboxes.append(box)
                return outboxes
            cropped_txts = stitchboxes(cropped_txts)
            for x1, y1, x2, y2 in cropped_txts:
                textprobs=[]
                for inverted in [1,0]:
                    image=cabin_cropped[y1:y2,x1:x2]
                    if inverted:
                        image=image[::-1,::-1]
                    text,prob=OCR(image)
                    textprobs.append([text,prob])
                print(textprobs)
                textorig=max(textprobs,key=lambda x:x[1])[0]
                drawtext(x1, y1, x2, y2, frame_cpy, x0, y0,textorig)
                
    cv2.imwrite('/tmp/pmnrs1.jpg',frame_cpy)
    cv2.imshow('',frame_cpy)
    cv2.waitKey(0)
    import time
    time.sleep(0.5)
