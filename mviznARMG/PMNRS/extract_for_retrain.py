import sys
from cabindetect import *
from textdetect import *
import SharedArray as sa
from datetime import datetime,timedelta
from memcachehelper import memcacheRW as mcrw

import os
import glob
import cv2

vidfile=sys.argv[1]
outprefix=sys.argv[2]
outd=os.path.dirname(outprefix)
os.makedirs(outd,exist_ok=True)
cap=cv2.VideoCapture(vidfile)
numframeswithtxt=0
boxi=0
while True:
    ret,frame=cap.read()
    if not ret:break
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
        #print(cropped_txts)
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
            framehastext=0
            for x1, y1, x2, y2 in cropped_txts:
                if y2-y1<20:continue
                if (x2-x1)/(y2-y1)>10:continue
                image=cabin_cropped[y1:y2,x1:x2]
                text,prob=OCR(image)
                if len(text)<3:
                    continue
                else:
                    boxi+=1                
                    framehastext=1
                outfile=f'{outprefix}_{boxi}---{text}.jpg'
                cv2.imwrite(outfile,image)
                drawtext(x1, y1, x2, y2, frame_cpy, x0, y0,text)
            numframeswithtxt+=framehastext
            if numframeswithtxt>=5:
                break
    cv2.imshow('',frame_cpy)
    k=cv2.waitKey(1)
    if k==ord('q'):raise
if numframeswithtxt<5:
    raise

