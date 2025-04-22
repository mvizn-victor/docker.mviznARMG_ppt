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
#input_files=glob.glob("/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/7109/20190612 - 20190711/OVLS/*")+glob.glob("/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/7109/20190612 - 20190711/OVSS/*")+glob.glob("/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/7109/20190612 - 20190711/PMNLS/*")+glob.glob("/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/7109/20190612 - 20190711/PMNSS/*")
#basedir='/mnt/NFSDIR/YardVideos/20190701/'
#basedir='/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/7109/20190612 - 20190711'
#input_files=glob.glob(f'{basedir}/OVLS/*.*')+glob.glob(f'{basedir}/OVSS/*.*')+glob.glob(f'{basedir}/PMNLS/*.*')+glob.glob(f'{basedir}/PMNSS/*.*')
basedir='/mnt/NFSDIR/RawVideos/ARMG/pmnrs_test/*'
input_files=glob.glob(f'{basedir}/OVLS/*/*.*')+glob.glob(f'{basedir}/OVSS/*/*.*')+glob.glob(f'{basedir}/PMNLS/*/*.*')+glob.glob(f'{basedir}/PMNSS/*/*.*')
date_input_files=[]
os.makedirs('PMNRSLOGS',exist_ok=True)
#20190612_110000_7109_OVSS.txt
for input_file in input_files:
    basename=os.path.basename(input_file)
    crane, cam, ymd, hms = basename[:-4].split('_')
    date_input_files.append((crane,ymd+hms,input_file))
date_input_files.sort()
input_file=input_files[0]
for _,_,input_file in date_input_files:
    basename=os.path.basename(input_file)
    crane,cam,ymd,hms=basename[:-4].split('_')
    if 'LS' in cam:
        side='LS'
    else:
        side='SS'
    outtext=f'PMNRSLOGS/{crane}_{ymd}_{hms}_{cam}.txt'
    if os.path.exists(outtext):
        continue

    baseouttext=os.path.basename(outtext)
    #if baseouttext!='7109_20190815_080000_OVSS.txt':
    #if not baseouttext.startswith('20190619_020000'):
    #    continue
    open(outtext, 'w')
    hms=hms
    videotime=datetime.strptime(ymd+hms,'%Y%m%d%H%M%S')
    lastvideotime=videotime
    cap = cv2.VideoCapture(input_file)
    #fps=cap.get(cv2.CAP_PROP_FPS)
    #print(fps)
    from collections import defaultdict
    texts=defaultdict(int)
    while True:
        ret, frame=cap.read()
        videotime=videotime+timedelta(seconds=1/13)
        if not ret:break
        #if videotime.minute<35:continue
        if videotime-lastvideotime>=timedelta(seconds=1):
            lastvideotime=videotime
        else:
            continue
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
                text = doOCR(cabin_cropped, [[x1, y1, x2, y2]], frame_cpy, x0, y0)
                print(crane,side,datetime.strftime(videotime,'%Y%m%d%H%M%S'),text,x0,y0,x1,y1,x2,y2,file=open(outtext,'a'))
            #print(len(cropped_txts))
            #cv2.imshow("Cabin", cabin_cropped_cpy)
        cv2.imshow("Video", cv2.resize(frame_cpy,(960,540)))
        c=cv2.waitKey(1000)
        if c==ord('s'):
            #skip video
            break
        if c==ord('1'):
            for i in range(10):ret, frame = cap.read()
        if c==ord('2'):
            for i in range(20):ret, frame = cap.read()
        if c==ord('3'):
            for i in range(40):ret, frame = cap.read()
        if c==ord('4'):
            for i in range(80):ret, frame = cap.read()
        if c==ord('5'):
            for i in range(160):ret, frame = cap.read()
        if c==ord('6'):
            for i in range(320):ret, frame = cap.read()
        elif c==ord('q'):
            sys.exit(0)

    cap.release()
cv2.destroyAllWindows()
