#version:1
import cv2
import time
from yolohelper import detect as YOLO
from memcachehelper import memcacheRW as mcrw
def drawCabinBoxes(frame, results):
    for result in results:
        # print(result)
        name = result[0]
        if type(name) == bytes:
            name = name.decode('utf8')
        prob = result[1]
        xc = int(result[2][0])
        yc = int(result[2][1])
        boxh = result[2][3]
        boxw = result[2][2]

        x1 = xc - int(boxw / 2)
        y1 = yc - int(boxh / 2)
        x2 = xc + int(boxw / 2)
        y2 = yc + int(boxh / 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (66, 66, 244), 3)

def drawCabinBoxes_cabins(frame, cabins):
    for cabin in cabins:
        # print(result)
        x1,y1,x2,y2=cabin
        cv2.rectangle(frame, (x1, y1), (x2, y2), (66, 66, 244), 3)


def detectCabins(frame):
    results = YOLO.inferImg(np_image=frame, thresh=0.65,
                        configPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.cfg",
                        weightPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.weights",
                        metaPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.data")
    cabin_cropped = None

    x1 = 0
    y1 = 0
    if len(results) == 1:
        result = results[0]
        xc = int(result[2][0])
        yc = int(result[2][1])
        boxh = result[2][3]
        boxw = result[2][2]

        x1 = max(0, xc - int(boxw / 2))
        y1 = max(0, yc - int(boxh / 2))
        x2 = xc + int(boxw / 2)
        y2 = yc + int(boxh / 2)

        if boxw > 2 and boxh > 2:
            cabin_cropped = frame[y1:y2, x1:x2]

    return results, cabin_cropped, (x1,y1)


def detectCabins_mcrw(frame, camid):
    if 0:
        results = YOLO.inferImg(np_image=frame, thresh=0.65,
                                configPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.cfg",
                                weightPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.weights",
                                metaPath="/home/mvizn/Code/mviznARMG/PMNRS/weights/PMNRS.data")
    results1, T = mcrw.raw_read(f'{camid}_yolo', [[], 0])
    if time.time()-T>1:
        print('yolo stale by',time.time()-T)
        results1=[]
    cabins=[]
    for result in results1:
        name = result[0]
        if type(name) == bytes:
            name = name.decode('utf8')
        if name=='t':
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = result[2][3]
            boxw = result[2][2]
            x1 = max(0, xc - int(boxw / 2))
            y1 = max(0, yc - int(boxh / 2))
            x2 = xc + int(boxw / 2)
            y2 = yc + int(boxh / 2)
            if boxw > 2 and boxh > 2:
                cabins.append([x1,y1,x2,y2])
    cabins.sort()
    if 'l' in camid:
        #landside leftmost
        cabins=cabins[:1]
    else:
        #seaside rightmost
        cabins=cabins[-1:]
    cabin_cropped = None
    x1 = 0
    y1 = 0
    if len(cabins) == 1:
        x1,y1,x2,y2=cabins[0]
        cabin_cropped = frame[y1:y2, x1:x2]

    return cabins, cabin_cropped, (x1, y1)

def detectCabins_procimage(frame, camid):
    from Utils.helper import procimage
    results1=procimage('hncdstopyolo',frame)
    cabins=[]
    for result in results1:
        name = result[0]
        if type(name) == bytes:
            name = name.decode('utf8')
        if name=='t':
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = result[2][3]
            boxw = result[2][2]
            x1 = max(0, xc - int(boxw / 2))
            y1 = max(0, yc - int(boxh / 2))
            x2 = xc + int(boxw / 2)
            y2 = yc + int(boxh / 2)
            if boxw > 2 and boxh > 2:
                cabins.append([x1,y1,x2,y2])
    cabins.sort()
    if 'l' in camid:
        #landside leftmost
        cabins=cabins[:1]
    else:
        #seaside rightmost
        cabins=cabins[-1:]
    cabin_cropped = None
    x1 = 0
    y1 = 0
    if len(cabins) == 1:
        x1,y1,x2,y2=cabins[0]
        cabin_cropped = frame[y1:y2, x1:x2]
    print('cabins:',cabins,camid)
    return cabins, cabin_cropped, (x1, y1)



