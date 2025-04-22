#version:1
from collections import defaultdict
from datetime import datetime, timedelta
import time
import cv2
import os
import SharedArray as sa
from Utils.helper import dummyimage,waittillvalidimage
import glob
import pickle
import GPUtil
if len(GPUtil.getGPUs())>1:
    os.environ["CUDA_VISIBLE_DEVICES"] = '1'
else:
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'

if os.path.exists('config/usecv2dnn'):
    from Utils.cv2dnn import *
    usecv2dnn=1
else:
    from yolohelper import detect as YOLO
    usecv2dnn=0
if usecv2dnn:
    yolo=YOLO("CLPS/weights/CLPS.weights")
    yolo.inferold(dummyimage)
    while True:
        try:
            f=min(glob.glob('/dev/shm/clps_yolo/*.jpg'))
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
                res = yolo.inferold(frame) 
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

else:
    results = YOLO.inferImg(np_image=dummyimage, thresh=0.2,
                            configPath="CLPS/weights/CLPS.cfg",
                            weightPath="CLPS/weights/CLPS.weights",
                            metaPath="CLPS/weights/CLPS.data")
    while True:
        try:
            f=min(glob.glob('/dev/shm/clps_yolo/*.jpg'))
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
                            configPath="CLPS/weights/CLPS.cfg",
                            weightPath="CLPS/weights/CLPS.weights",
                            metaPath="CLPS/weights/CLPS.data")
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

