import pickle
import os

os.environ['CUDA_VISIBLE_DEVICES']='0'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'
import numpy as np
import glob
import cv2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import os
import time
Tstart=time.time()

classnames = ['c', 'l']
cfg = get_cfg()
cfg.merge_from_file("/home/mvizn/Code/detectron2_repo/configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.WEIGHTS = '/mnt/NFSDIR/ARMG-Project-Data/CLPS/images_2020-08-18_model/model_0054999.pth'
cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(classnames)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8   # set the testing threshold for this model
predictor = DefaultPredictor(cfg)
def detectmodel(frame):
    outputs = predictor(frame)
    r00=outputs["instances"].to("cpu").get_fields()
    r0=dict()
    r0['class_ids']=r00['pred_classes']+1
    masks=np.bool8(r00['pred_masks'].numpy())
    masks=np.moveaxis(masks,[0],[2])
    r0['masks']=masks
    return r0
from Utils.helper import dummyimage,waittillvalidimage

res = detectmodel(dummyimage)
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
            res = detectmodel(frame)
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

