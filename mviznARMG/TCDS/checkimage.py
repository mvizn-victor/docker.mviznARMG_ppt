import cv2
from yolohelper import detect as YOLO
import SharedArray as sa
from tfstuff import infer
import tensorflow as tf
import glob
import re
import numpy as np
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)
#imgfiles=natural_sort(glob.glob('/mnt/NFSDIR/ARMG-Project-Data/TCDS_images/*'))
imgfiles=natural_sort(glob.glob('/home/mvizn/Code/imagesorter/static/tcds*/**/*.jpg',recursive=True))
import random
random.shuffle(imgfiles)
tfconfig = tf.ConfigProto(
        device_count = {'GPU': 1}
    )
tfconfig.gpu_options.allow_growth = True
verbose=0
out=[]
with tf.Session(config=tfconfig, graph=infer.graph) as sess:
    infer.get_top_res(sess, np.zeros((3,3,3)))
    for f in imgfiles:
        frame=cv2.imread(f)
        frame2=frame
        frame3=frame[:,:,::-1]
        res = infer.get_top_res(sess, frame2)
        res2 = infer.get_top_res(sess, frame3)
        with open('/tmp/res.txt','a') as fout:
            print(f,res[0],res[1],res2[0],res2[1],file=fout)