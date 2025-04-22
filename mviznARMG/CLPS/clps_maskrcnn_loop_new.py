import pickle
import os

os.environ['CUDA_VISIBLE_DEVICES']='0'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'
import sys
sys.path.append('Mask_RCNN')
import numpy as np
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from mrcnn import visualize
import glob
import cv2
model_path='/home/mvizn/Code/Mask_RCNN/samples/voc_clps_20191202/logs/voc20200915T1448/mask_rcnn_voc_0160.h5'
import time
Tstart=time.time()
VOC_CLASSES = ['_background_', 'c', 'l']
class VocConfig(Config):
    NAME = "voc"

    IMAGE_PER_GPU = 2

    NUM_CLASSES = len(VOC_CLASSES)  # VOC 2012 have 20 classes. "1" is for background.

    STEPS_PER_EPOCH = 100

    if 'resnet50' in model_path:
        BACKBONE='resnet50'
class InferenceConfig(VocConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    DETECTION_MIN_CONFIDENCE = 0.8


config = InferenceConfig()

model=modellib.MaskRCNN(mode='inference',config=config,model_dir='')
model.load_weights(model_path, by_name=True)
import os
from Utils.helper import dummyimage,waittillvalidimage
res = model.detect([dummyimage], verbose=0)[0]
print('init takes',time.time()-Tstart)
while True:
    try:
        f=min(glob.glob('/dev/shm/clpsmaskrcnn/*.jpg'))
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
            Tstart=time.time()
            res = model.detect([frame], verbose=0)[0]
            print('inference takes', time.time() - Tstart)
            print(5)
            #print(res)
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

