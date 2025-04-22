#version:1
from collections import defaultdict
from datetime import datetime, timedelta
import time
import cv2
import os
from yolohelper import detect as YOLO
import SharedArray as sa
from Utils.helper import dummyimage,waittillvalidimage
import glob
import pickle
results = YOLO.inferImg(np_image=dummyimage, thresh=0.4,
                        configPath="HNCDS/weights/HNCDSside.cfg",
                        weightPath="HNCDS/weights/HNCDSside.weights",
                        metaPath="HNCDS/weights/HNCDSside.data")
while True:
    try:
        f=min(glob.glob('/dev/shm/hncdssideyolo/*.jpg'))
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
            res = YOLO.inferImg(np_image=frame, thresh=0.2,
                        configPath="HNCDS/weights/HNCDSside.cfg",
                        weightPath="HNCDS/weights/HNCDSside.weights",
                        metaPath="HNCDS/weights/HNCDSside.data")
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
        time.sleep(0.001)
        pass

