#version:1
import sys
sys.path.append('/home/mvizn/Code/Mask_RCNN')
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from mrcnn import visualize

import matplotlib
# Agg backend runs without a display
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
model_path='CLPS/weights/clps.h5'


class VocConfig(Config):
    NAME = "voc"

    IMAGE_PER_GPU = 2

    NUM_CLASSES = 1 + 20  # VOC 2012 have 20 classes. "1" is for background.

    STEPS_PER_EPOCH = 100


class InferenceConfig(VocConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    DETECTION_MIN_CONFIDENCE = 0


VOC_CLASSES = ['_background_', 'c']
VocConfig.NUM_CLASSES = len(VOC_CLASSES)
InferenceConfig.NUM_CLASSES = len(VOC_CLASSES)
config = InferenceConfig()

model=modellib.MaskRCNN(mode='inference',config=config,model_dir='')
model.load_weights(model_path, by_name=True)

videof="CLPS/sample/40ft_1_f.mp4"
videob="CLPS/sample/40ft_1_b.mp4"
import cv2
capf=cv2.VideoCapture(videof)
capb=cv2.VideoCapture(videob)
framenum=0
cv2.namedWindow("f");
cv2.moveWindow("f", 0,0);
cv2.namedWindow("b");
cv2.moveWindow("b", 640,0);

while True:
    ret,framef=capf.read()
    ret,frameb=capb.read()
    if not ret:
        break
    c=cv2.waitKey(1)

    cv2.imshow('f',cv2.resize(framef,(640,360)))
    cv2.imshow('b',cv2.resize(frameb,(640,360)))

    if c==ord('q'):
        break
    framenum+=1