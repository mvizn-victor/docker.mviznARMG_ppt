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
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
import sys
sys.path.append('EAST')
import locality_aware_nms as nms_locality
import lanms
import model
from icdar import restore_rectangle
input_vid = '/mnt/NFSDIR/RawVideos/Yard-Tender-Videos/VA Pre-Assessment Videos/PMNRS-VA/IGH and EH/20FT Front/PMNSS 1228.avi'
ckpt_path = 'EAST/models/east_icdar2015_resnet_v1_50_rbox/'

def resize_image(im, max_side_len=2400):
    '''
    resize image to a size multiple of 32 which is required by the network
    :param im: the resized image
    :param max_side_len: limit of max image size to avoid out of memory in gpu
    :return: the resized image and the resize ratio
    '''
    h, w, _ = im.shape

    resize_w = w
    resize_h = h

    # limit the max side
    if max(resize_h, resize_w) > max_side_len:
        ratio = float(max_side_len) / resize_h if resize_h > resize_w else float(max_side_len) / resize_w
    else:
        ratio = 1.
    resize_h = int(resize_h * ratio)
    resize_w = int(resize_w * ratio)

    resize_h = resize_h if resize_h % 32 == 0 else (resize_h // 32 - 1) * 32
    resize_w = resize_w if resize_w % 32 == 0 else (resize_w // 32 - 1) * 32
    resize_h = max(32, resize_h)
    resize_w = max(32, resize_w)
    im = cv2.resize(im, (int(resize_w), int(resize_h)))

    ratio_h = resize_h / float(h)
    ratio_w = resize_w / float(w)

    return im, (ratio_h, ratio_w)


def detect(score_map, geo_map, timer, score_map_thresh=0.8, box_thresh=0.1, nms_thres=0.2):
    '''
    restore text boxes from score map and geo map
    :param score_map:
    :param geo_map:
    :param timer:
    :param score_map_thresh: threshhold for score map
    :param box_thresh: threshhold for boxes
    :param nms_thres: threshold for nms
    :return:
    '''
    if len(score_map.shape) == 4:
        score_map = score_map[0, :, :, 0]
        geo_map = geo_map[0, :, :, ]
    # filter the score map
    xy_text = np.argwhere(score_map > score_map_thresh)
    # sort the text boxes via the y axis
    xy_text = xy_text[np.argsort(xy_text[:, 0])]
    # restore
    start = time.time()
    text_box_restored = restore_rectangle(xy_text[:, ::-1]*4, geo_map[xy_text[:, 0], xy_text[:, 1], :]) # N*4*2
    print('{} text boxes before nms'.format(text_box_restored.shape[0]))
    boxes = np.zeros((text_box_restored.shape[0], 9), dtype=np.float32)
    boxes[:, :8] = text_box_restored.reshape((-1, 8))
    boxes[:, 8] = score_map[xy_text[:, 0], xy_text[:, 1]]
    timer['restore'] = time.time() - start
    # nms part
    start = time.time()
    # boxes = nms_locality.nms_locality(boxes.astype(np.float64), nms_thres)
    boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thres)
    timer['nms'] = time.time() - start

    if boxes.shape[0] == 0:
        return None, timer

    # here we filter some low score boxes by the average score map, this is different from the orginal paper
    for i, box in enumerate(boxes):
        mask = np.zeros_like(score_map, dtype=np.uint8)
        cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)
        boxes[i, 8] = cv2.mean(score_map, mask)[0]
    boxes = boxes[boxes[:, 8] > box_thresh]

    return boxes, timer


def sort_poly(p):
    min_axis = np.argmin(np.sum(p, axis=1))
    p = p[[min_axis, (min_axis+1)%4, (min_axis+2)%4, (min_axis+3)%4]]
    if abs(p[0, 0] - p[1, 0]) > abs(p[0, 1] - p[1, 1]):
        return p
    else:
        return p[[0, 3, 2, 1]]



def gettextboxes(im):
    start_time = time.time()
    im_resized, (ratio_h, ratio_w) = resize_image(im)

    timer = {'net': 0, 'restore': 0, 'nms': 0}
    start = time.time()
    score, geometry = sess.run([f_score, f_geometry], feed_dict={input_images: [im_resized]})
    timer['net'] = time.time() - start

    boxes, timer = detect(score_map=score, geo_map=geometry, timer=timer)
    print('net {:.0f}ms, restore {:.0f}ms, nms {:.0f}ms'.format(
        timer['net']*1000, timer['restore']*1000, timer['nms']*1000))

    if boxes is not None:
        boxes = boxes[:, :8].reshape((-1, 4, 2))
        boxes[:, :, 0] /= ratio_w
        boxes[:, :, 1] /= ratio_h

    duration = time.time() - start_time
    print('[timing] {}'.format(duration))

    # save to file
    outboxes=[]
    if boxes is not None:
        for box in boxes:
            # to avoid submitting errors
            box = sort_poly(box.astype(np.int32))
            if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3] - box[0]) < 5:
                continue
            #import pickle
            #pickle.dump(box,open('/tmp/1.pkl','wb'))
            #raise Exception('q')
            #cv2.polylines(im, [box.astype(np.int32).reshape((-1, 1, 2))], True, color=(255, 255, 0), thickness=4)
            #cv2.imshow("Output", im)
            #cv2.waitKey(1)
            x1 = max(int(min(box[:, 0])), 0)
            y1 = max(int(min(box[:, 1])), 0)
            x2 = int(max(box[:, 0]))
            y2 = int(max(box[:, 1]))
            w=x2-x1
            h=y2-y1
            x1 = max(int(x1 - w * .05),0)
            x2 = int(x2 + w * .05)
            y1 = max(int(y1 - h * .05),0)
            y2 = int(y2 + h * .05)
            outboxes.append((x1, y1, x2, y2))
    return outboxes

if __name__=='__main__':

    import platform
    import GPUtil
    import os

    input_images = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_images')
    global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

    f_score, f_geometry = model.model(input_images, is_training=False)

    variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
    saver = tf.train.Saver(variable_averages.variables_to_restore())

    config = tf.ConfigProto()
    #config.gpu_options.allow_growth = True
    if len(GPUtil.getGPUs())>1:
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
        config.gpu_options.per_process_gpu_memory_fraction = 2./8
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
        config.gpu_options.per_process_gpu_memory_fraction = 2./11
    config.allow_soft_placement = True
    sess=tf.Session(config=config)
    ckpt_state = tf.train.get_checkpoint_state(ckpt_path)
    model_path = os.path.join(ckpt_path, os.path.basename(ckpt_state.model_checkpoint_path))
    print('Restore from {}'.format(model_path))
    saver.restore(sess, model_path)
    #preload
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
