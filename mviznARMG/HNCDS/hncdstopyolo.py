#version:fi21
from collections import defaultdict
from datetime import datetime, timedelta
import time
import cv2
import os
import SharedArray as sa
from Utils.helper import dummyimage,waittillvalidimage
import glob
import pickle

if os.path.exists('config/usecv2dnn'):
    from Utils.cv2dnn import YOLO as CV2YOLO
    class YOLOdarknet:
        cv2yolo=None
        def inferImg(self,weightPath,thresh,np_image=None,**kwargs):
            if np_image is None:
                np_image=np.zeros((3,3,3),dtype=np.uint8)
            if self.cv2yolo is None:
                self.cv2yolo=CV2YOLO(weightPath)
            return self.cv2yolo.inferold(np_image,thresh=thresh)
    YOLO=YOLOdarknet()
else:
    from yolohelper import detect as YOLO

results = YOLO.inferImg(np_image=dummyimage, thresh=0.2,
                        configPath="HNCDS/weights/HNCDS.cfg",
                        weightPath="HNCDS/weights/HNCDS.weights",
                        metaPath="HNCDS/weights/HNCDS.data")
while True:
    try:
        f=min(glob.glob('/dev/shm/hncdstopyolo/*.jpg'))
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
                        configPath="HNCDS/weights/HNCDS.cfg",
                        weightPath="HNCDS/weights/HNCDS.weights",
                        metaPath="HNCDS/weights/HNCDS.data")
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

