#version:1
import time
import cv2
import pickle
import os
import glob
import platform
import GPUtil
from Utils.helper import dummyimage,waittillvalidimage
if os.path.exists('config/usecv2dnn'):
    from Utils.cv2dnn import *
    usecv2dnn=1
else:
    from tfstuff import clpslift_infer as infer
    import tensorflow as tf
    usecv2dnn=0
print('usecv2dnn',usecv2dnn)
if usecv2dnn:
    if len(GPUtil.getGPUs())>1:
        os.environ["CUDA_VISIBLE_DEVICES"] = '1'
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    inception=Inception('CLPS/weights/clpslift.pb')
    res=inception.infer(dummyimage)
    print('dummy',res)
    if 1:
        while True:
            try:
                f=min(glob.glob('/dev/shm/clpslift_inception/*.jpg'))
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
                    res=inception.infer(frame)
                    print(5)
                    print(res)
                    print(6)
                    pickle.dump(res,open(fout,'wb'))
                    print(7)
                else:
                    res=infer.get_top_res_file(sess,f)
                    os.unlink(f)
                    fout = f.replace('.jpg', '.pkl')
                    print(res)
                    pickle.dump(res, open(fout, 'wb'))
            except ValueError:
                time.sleep(0.001)
                pass
            except Exception as e:
                print(e.__class__,e)
                time.sleep(0.001)
                pass
else:
    tfconfig = tf.ConfigProto(
            device_count = {'GPU': 1}
        )
    if len(GPUtil.getGPUs())>1:
        os.environ["CUDA_VISIBLE_DEVICES"] = '1'
        tfconfig.gpu_options.per_process_gpu_memory_fraction = 1. / 8
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
        tfconfig.gpu_options.per_process_gpu_memory_fraction = 0.5 / 11
    verbose=0
    with tf.Session(config=tfconfig, graph=infer.graph) as sess:
        #preload
        from Utils.helper import dummyimage,waittillvalidimage
        res=infer.get_top_res(sess, dummyimage)
        print('dummy',res)
        while True:
            try:
                f=min(glob.glob('/dev/shm/clpslift_inception/*.jpg'))
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
                    res=infer.get_top_res(sess, frame)
                    print(5)
                    print(res)
                    print(6)
                    pickle.dump(res,open(fout,'wb'))
                    print(7)
                else:
                    res=infer.get_top_res_file(sess,f)
                    os.unlink(f)
                    fout = f.replace('.jpg', '.pkl')
                    print(res)
                    pickle.dump(res, open(fout, 'wb'))
            except ValueError:
                time.sleep(0.001)
                pass
            except Exception as e:
                print(e.__class__,e)
                time.sleep(0.001)
                pass
