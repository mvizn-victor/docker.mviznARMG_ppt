extract=0
import os
import cv2

from yolohelper import detect as YOLO
from shapely.geometry import Polygon,box
from Utils.helper import *
import SharedArray as sa
#ovls=sa.attach('shm://ovls_raw')
#while True:
#    frame=ovls.copy()
import glob
#files=glob.glob('/home/mvizn/Desktop/tmp/*.mp4')
import sys
if len(sys.argv)<2:
    files=['HNCDS/sample/1.mp4']
else:
    files=[sys.argv[1]]
    camname=sys.argv[2]
    SIDE=camname[-2]
    if len(sys.argv)>=4:
        outfile=sys.argv[3]
    else:
        outfile='/tmp/out.mp4'
pthresh=0.2
athresh=0.2
hthresh=0.2
cthresh=0.2
for f in files*1:
    print(f)
    cap=cv2.VideoCapture(f)    
    framenum = 0
    while True:
        ret,frame=cap.read()
        framenum+=1
        #if framenum<90*25:continue
        if not ret:break
        if framenum==1:
            vidh,vidw=frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"MP4V")
            vidout = cv2.VideoWriter(outfile, fourcc, 5, (vidw,vidh))

        frame_cpy=frame.copy()
        results = YOLO.inferImg(np_image=frame, thresh=0.2,
                            configPath="HNCDS/weights/HNCDS.cfg",
                            weightPath="HNCDS/weights/HNCDS.weights",
                            metaPath="HNCDS/weights/HNCDS.data")

        def getcabins():
            cabins = []
            for result in results:
                name = result[0]
                if type(name) == bytes:
                    name = name.decode('utf8')
                if name == 't':
                    xc = int(result[2][0])
                    yc = int(result[2][1])
                    boxh = int(result[2][3] / 2)
                    boxw = int(result[2][2] / 2)
                    x1 = xc - boxw
                    y1 = yc - boxh
                    x2 = xc + boxw
                    y2 = yc + boxh
                    cabins.append([x1, y1, x2, y2])
            return cabins

        cabins = getcabins()
        # left most for land side
        # right most for sea side
        cabins.sort()
        if SIDE == 'l':
            cabins = cabins[:1]
        elif SIDE == 's':
            cabins = cabins[-1:]

        if camname in ['ovls', 'ovss']:
            for cabini, cabin in enumerate(cabins):
                va = 0
                vh = 0
                vp = 0
                x1, y1, x2, y2 = cabin
                w = x2 - x1
                h = y2 - y1
                minx = max(0, int(x1 - w))
                maxx = int(x2 + w)
                miny = max(0, int(y1 - h))
                maxy = int(y2 + h)
                framecabin = frame[miny:maxy, minx:maxx]
                framecabin_cpy = framecabin.copy()
                results = YOLO.inferImg(np_image=framecabin, thresh=0.2,
                                        configPath="HNCDS/weights/HNCDS.cfg",
                                        weightPath="HNCDS/weights/HNCDS.weights",
                                        metaPath="HNCDS/weights/HNCDS.data")
                print(cabini, results)


                def getcabins():
                    cabins = []
                    for result in results:
                        name = result[0]
                        if type(name) == bytes:
                            name = name.decode('utf8')
                        if name == 't':
                            xc = int(result[2][0])
                            yc = int(result[2][1])
                            boxh = int(result[2][3] / 2)
                            boxw = int(result[2][2] / 2)
                            x1 = xc - boxw
                            y1 = yc - boxh
                            x2 = xc + boxw
                            y2 = yc + boxh
                            cabins.append([x1, y1, x2, y2])
                    return cabins


                cabins_ = getcabins()
                for result in results:
                    name = result[0]
                    if type(name) == bytes:
                        name = name.decode('utf8')
                    prob = result[1]
                    xc = int(result[2][0])
                    yc = int(result[2][1])
                    boxh = int(result[2][3] / 2)
                    boxw = int(result[2][2] / 2)
                    SIZE = max(boxw, boxh) * 2
                    x1 = xc - boxw
                    y1 = yc - boxh
                    x2 = xc + boxw
                    y2 = yc + boxh

                    if name == 'p' and prob >= pthresh:
                        # if overlap with cabin name='h'
                        overlapcabin = False
                        for (x1_, y1_, x2_, y2_) in cabins_:
                            eps = 1  # (x2_-x1_)/10
                            # door is on cabin right, human detected near right side of cabin considered as head
                            if box(x2_, y1_, x2_ + eps, y2_).intersects(box(x1, y1, x2, y2)):
                                overlapcabin = True
                                print('overlapcabin')
                        if overlapcabin:
                            name = 'h'
                        else:
                            name = 'p'

                    if name == 'a' and prob >= athresh or name == 'c' and prob >= cthresh:
                        va = 1
                        todraw = 1
                        #mcrw.raw_write('last_hncds_a', time.time())
                    elif name == 'h' and prob >= hthresh:
                        vh = 1
                        #mcrw.raw_write('last_hncds_h', time.time())
                        todraw = 1
                    elif name == 'p' and prob >= pthresh:
                        vp = 1
                        #mcrw.raw_write('last_hncds_p', time.time())
                        todraw = 1
                    elif name == 't':
                        todraw = 1
                    else:
                        todraw = 0
                    if name == 'a' or name == 'c': color = (255, 0, 0)
                    if name == 'h': color = (0, 255, 0)
                    if name == 'p': color = (0, 0, 255)
                    if name == 't': color = (255, 255, 0)
                    if todraw:
                        cv2.rectangle(framecabin_cpy, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(framecabin_cpy, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (255, 0, 0), 2)



            try:
                cv2.imshow('', framecabin_cpy)
                imout = np.zeros((vidh, vidw, 3), np.uint8)
                assignscaleimage(imout,framecabin_cpy)
                vidout.write(imout)
            except:
                pass
            if extract:
                bname = os.path.basename(f)
                cv2.imwrite(f'/mnt/NFSDIR/hncdstrain/photos/{bname}_{framenum}.jpg', framecabin)
        else:        
            for result in results:
                name = result[0]
                if type(name) == bytes:
                    name = name.decode('utf8')
                prob = result[1]
                xc = int(result[2][0])
                yc = int(result[2][1])
                boxh = int(result[2][3] / 2)
                boxw = int(result[2][2] / 2)
                SIZE = max(boxw, boxh) * 2
                x1 = xc - boxw
                y1 = yc - boxh
                x2 = xc + boxw
                y2 = yc + boxh

                if name == 'a' and prob >= athresh or name == 'c' and prob >= cthresh:
                    va = 1
                    todraw = 1
                    #mcrw.raw_write('last_hncds_a', time.time())
                elif name == 'h' and prob >= hthresh:
                    vh = 1
                    #mcrw.raw_write('last_hncds_h', time.time())
                    todraw = 1
                elif name == 'p' and prob >= pthresh:
                    vp = 1
                    #mcrw.raw_write('last_hncds_p', time.time())
                    todraw = 1
                elif name == 't':
                    todraw = 1
                else:
                    todraw = 0
                if name == 'a' or name == 'c': color = (255, 0, 0)
                if name == 'h': color = (0, 255, 0)
                if name == 'p': color = (0, 0, 255)
                if name == 't': color = (255, 255, 0)
                if todraw:
                    cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame_cpy, f'{name}:{prob:.2f}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 2)

        
            cv2.imshow('',frame_cpy)
            vidout.write(frame_cpy)
            if extract:
                bname = os.path.basename(f)
                cv2.imwrite(f'/mnt/NFSDIR/hncdstrain/photos/{bname}_{framenum}.jpg', frame)
        c=cv2.waitKey(1)
        if c==ord('q'):
            raise('q')
        if c==ord('s'):
            break
vidout.release()
