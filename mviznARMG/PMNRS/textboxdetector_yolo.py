import pickle
import glob
import requests
import base64
import cv2
import time
import math
import os
#os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'
import numpy as np
#import tensorflow as tf
import sys
from yolohelper import detect as YOLO

def gettextboxes(im):
    start_time = time.time()
    results=YOLO.inferImg(np_image=im, thresh=0.2,
                            configPath="PMNRS/weights/PMNRS2.cfg",
                            weightPath="PMNRS/weights/PMNRS2.weights",
                            metaPath="PMNRS/weights/PMNRS2.data")
    duration = time.time() - start_time
    print('[timing] {}'.format(duration))
    outboxes=[]    
    for result in results:
        name = result[0]
        if type(name) == bytes:
            name = name.decode('utf8')
        prob = result[1]
        xc = int(result[2][0])
        yc = int(result[2][1])
        boxh = int(result[2][3] / 2)
        boxw = int(result[2][2] / 2)
        x1 = max(xc - boxw,0)
        y1 = max(yc - boxh,0)
        x2 = xc + boxw
        y2 = yc + boxh        
        # save to file
        outboxes.append((x1,y1,x2,y2))
    return outboxes

if __name__=='__main__':
    from Utils.helper import dummyimage,waittillvalidimage
    res=gettextboxes(dummyimage)
    verbose=0
    while 1:
        try:
            f=min(glob.glob('/dev/shm/pmnrstextdetect/*.jpg'))
            if 1:
                print(0)
                if not waittillvalidimage(f):
                    os.unlink(f)
                    print('invalid image')
                    continue
                print(1)
                frame=cv2.imread(f)
                frame.shape
                print(2)
                os.unlink(f)
                print(3)
                fout=f.replace('.jpg','.pkl')
                print(4)
                res=gettextboxes(frame)
                print(5)
                print(res)
                print(6)
                pickle.dump(res,open(fout,'wb'))
                print(7)
        except ValueError:
            time.sleep(0.001)
            pass
        except Exception as e:
            print(e.__class__,e)
            pass
