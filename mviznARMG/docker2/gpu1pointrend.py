helperfunprint=0
#%run -i /home/mvizn/helperfun.py
from vcutils.helperfun import *
progress1=Progress()
progress2=Progress()
progress3=Progress()
#######CHANGE HERE 1
procname='clpsmaskrcnn'
os.system(f'rm /dev/shm/{procname}/*.jpg')


#######CHANGE HERE 2
Dpointrend='CLPS/weights'


import numpy as np
import cv2
import pickle
import os
import glob
import GPUtil

if len(GPUtil.getGPUs())==2:
    os.environ['CUDA_VISIBLE_DEVICES']='1'
else:
    os.environ['CUDA_VISIBLE_DEVICES']='0'

os.environ['TF_FORCE_GPU_ALLOW_GROWTH']='true'
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import sys
sys.path.insert(1, "detectron2_repo/projects/PointRend")
import point_rend
import os
import time


#######CHANGE HERE 3
classnames = open(f'{Dpointrend}/classes.txt').read().strip().split()
#classnames=['c','l']

cfg = get_cfg()
point_rend.add_pointrend_config(cfg)
cfg.merge_from_file("detectron2_repo/projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml")

#######CHANGE HERE 4
cfg.MODEL.WEIGHTS = f'{Dpointrend}/clps_pointrend.pth'

cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(classnames)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8   # set the testing threshold for this model
cfg.MODEL.POINT_HEAD.NUM_CLASSES = len(classnames)
predictor = DefaultPredictor(cfg)
def makedirsf(f):
    D=os.path.dirname(f)
    os.makedirs(D,exist_ok=True)
    return f
def makedirs_imwrite(f,im):
    makedirsf(f)
    cv2.imwrite(f,im)
def detectmodel(frame):
    outputs = predictor(frame)
    global r00
    r00=outputs["instances"].to("cpu").get_fields()
    r0=dict()
    r0['class_ids']=np.array(r00['pred_classes']+1)
    masks=np.bool8(r00['pred_masks'].numpy())
    masks=np.moveaxis(masks,[0],[2])
    r0['masks']=masks
    r0['pred_boxes']=np.array(r00['pred_boxes'].tensor)
    return r0
#print1=print
#print0=print
def print0(*args,**kwargs):
    print(procname,*args,**kwargs)
print0('print0 test')
print('print test')

status={}
status['T']=0
status['start']=0
status['end']=0
status['i1']=0
status['i2']=0
status['i3']=0
status['i4']=0
status['i5']=0
status['f']=''
status['s']=''
sio=io.StringIO()
while True:
    def fun1():
        status['T']=time.time()
        print0(datetime.now())
        print0('heartbeat1')
        print0('start',status['start'])
        print0('i1',status['i1'])
        print0('i2',status['i2'])
        print0('i3',status['i3'])
        print0('i4',status['i4'])
        print0('i5',status['i5'])
        print0('end',status['end'])
        print0('f',status['f'])
        print0(status['s'])
    progress1.do(fun1)
    status['start']+=1
    try:
        procname                
        try:
            f=min(glob.glob(f'/dev/shm/{procname}/*.jpg'))
            status['f']=f
            if time.time()-os.path.getmtime(f)>11:
                try:
                    print0('remove',f,'age',time.time()-os.path.getmtime(f))
                    os.unlink(f)
                except Exception as e:
                    printerror(e,print=print0)
                    pass
                continue
        except:
            #no files in queue ignore error
            raise MyExc('e1')
        if 1:
            sio=io.StringIO()
            #print1=print0
            print1=printfile(sio)
            print1(0)
            T=time.time()
            status['i1']+=1
            if not waittillvalidimage(f):
                os.unlink(f)
                print1('invalid image')
                continue
            status['i2']+=1

            T=time.time()
            frame=cv2.imread(f)
            print1('frame.shape',frame.shape)
            os.unlink(f)
            fout=f.replace('.jpg','.pkl')
            T=time.time()
            status['i3']+=1
            res = detectmodel(frame)
            print1('res',res)
            T=time.time()
            pickle.dump(res,open(fout,'wb'))
            status['i4']+=1

            def fun2():
                print0('verbose with 1 second cooldown')
                print0(getvalue(sio))
            progress2.do(fun2)
    except kbi:
        raise
    except MyExc as e:
        if e.args[0]=='e1':
            pass
    except Exception as e:
        def fun3():
            print0('<sio>')
            print0(getvalue(sio))
            print0('</sio>')
            printerror(e,print=print0)
        progress3.do(fun3)

    status['end']+=1
    time.sleep(0.001)
