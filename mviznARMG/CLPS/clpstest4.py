from config.config import *
import SharedArray as sa

import os
import heapq
# os.environ['CUDA_VISIBLE_DEVICES']='1'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

import sys

sys.path.append('Mask_RCNN')
import numpy as np
from mrcnn.config import Config
from mrcnn import model as modellib, utils
from mrcnn import visualize
import matplotlib
# Agg backend runs without a display
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import cv2

plt.rcParams['figure.figsize'] = [20, 10]
# model_path='CLPS/weights/clps.h5'
# model_path='CLPS/weights/clps.h5'
model_path = '/home/mvizn/Code/mviznARMG/CLPS/weights/clps.h5'


class VocConfig(Config):
    NAME = "voc"

    IMAGE_PER_GPU = 2

    NUM_CLASSES = 1 + 20  # VOC 2012 have 20 classes. "1" is for background.

    STEPS_PER_EPOCH = 100
    if 'resnet50' in model_path:
        BACKBONE = 'resnet50'
    # IMAGE_MIN_DIM=64
    # IMAGE_MAX_DIM=64
    # MAX_GT_INSTANCES=2


class InferenceConfig(VocConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    DETECTION_MIN_CONFIDENCE = 0


print(VocConfig.IMAGE_MIN_DIM)
print(InferenceConfig.IMAGE_MIN_DIM)
VOC_CLASSES = ['_background_', 'c']
VocConfig.NUM_CLASSES = len(VOC_CLASSES)
InferenceConfig.NUM_CLASSES = len(VOC_CLASSES)
config = InferenceConfig()

model = modellib.MaskRCNN(mode='inference', config=config, model_dir='')
model.load_weights(model_path, by_name=True)
if 0:
    while True:
        model.detect([np.zeros((1024, 1024, 3))], verbose=0)[0]
        pass


def maskoutcontainer(image0, maskout=True, maskfile=False):
    T0=time.time()
    r0 = model.detect([image0], verbose=0)[0]
    print('maskout modeldetect:', time.time() - T0)
    if maskfile:
        _, ax = plt.subplots(1, figsize=(16, 16))
        visualize.display_instances(
            image0, r0['rois'], r0['masks'], r0['class_ids'],
            VOC_CLASSES, r0['scores'],
            show_bbox=True, show_mask=True, ax=ax,
            title="Predictions")
        plt.savefig(maskfile)
        plt.close()
        print('maskout drawmask:', time.time() - T0)
    newmask = np.zeros(image0.shape[:2], dtype=bool)
    for maski in range(len(r0['class_ids'])):
        mask = r0['masks'][:, :, maski]
        for i in range(mask.shape[1]):
            try:
                newmask[0:np.max(np.argwhere(mask[:, i] == 1)), i] = 1
            except:
                pass
    # newmask[:,0:np.min(np.argwhere(newmask),axis=0)[1]]=1
    # newmask[:,np.max(np.argwhere(newmask),axis=0)[1]:]=1
    newmask[:, np.max(newmask, axis=0) == False] = 1
    if maskout:
        image0[newmask] = 0
    print('maskout newmask:', time.time() - T0)
    return newmask


def bsmatcher(image0, image1, newmask0, newmask1, draw=False, sift0=None):
    T0 = time.time()
    import numpy as np
    import cv2 as cv
    import matplotlib.pyplot as plt
    # img1 = cv.imread('box.png',cv.IMREAD_GRAYSCALE)          # queryImage
    # img2 = cv.imread('box_in_scene.png',cv.IMREAD_GRAYSCALE) # trainImage
    img1 = image0.copy()
    img2 = image1.copy()
    print("bsmatcher copy:", time.time() - T0)
    img1[newmask0] = 0
    img2[newmask1] = 0
    # Initiate SIFT detector
    sift = cv.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    if sift0 is not None:
        kp1, des1 = sift0
    else:
        kp1, des1 = sift.detectAndCompute(img1, None)

    kp2, des2 = sift.detectAndCompute(img2, None)
    print("bsmatcher sift:", time.time() - T0)
    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary
    flann = cv.FlannBasedMatcher(index_params, search_params)
    try:
        matches = flann.knnMatch(des1, des2, k=2)
    except:
        matches = []
    # Need to draw only good matches, so create a mask
    matchesMask = [[0, 0] for i in range(len(matches))]
    # ratio test as per Lowe's paper
    print('matches', len(matches))
    print("bsmatcher FlannBasedMatcher:", time.time() - T0)
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            x1, y1 = cv2.KeyPoint_convert(kp1)[m.queryIdx]
            x1, y1 = int(x1), int(y1)
            x2, y2 = cv2.KeyPoint_convert(kp2)[m.trainIdx]
            x2, y2 = int(x2), int(y2)
            if True or not newmask0[y1, x1] and not newmask1[y2, x2]:
                matchesMask[i] = [1, 0]
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=(255, 0, 0),
                       matchesMask=matchesMask,
                       flags=cv.DrawMatchesFlags_DEFAULT)
    if draw:
        img3 = cv.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)
        plt.imshow(img3)
    print("bsmatcher filtermatches:", time.time() - T0)
    out = []
    for match in list(matches[i][0] for i in np.argwhere(np.array(matchesMask))[:, 0]):
        # print(cv2.KeyPoint_convert(kp1)[match.queryIdx],cv2.KeyPoint_convert(kp2)[match.trainIdx])
        # out.append(abs(cv2.KeyPoint_convert(kp1)[match.queryIdx][1]-cv2.KeyPoint_convert(kp2)[match.trainIdx][1]))
        out.append([cv2.KeyPoint_convert(kp1)[match.queryIdx], cv2.KeyPoint_convert(kp2)[match.trainIdx]])
    print("bsmatcher export matches:", time.time() - T0)
    return out, cv2.KeyPoint_convert(kp2), (kp2, des2)


from scipy.spatial.distance import cdist


def dist(x, y):
    return cdist([x], [y])[0][0]


def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]


def mindist(node, nodes):
    try:
        d = cdist([node], nodes)
        mind = d.min()
        argmind = d.argmin()
    except:
        mind = 9999
        argmind = None
    return mind, argmind


def withindist(node, nodes, threshold):
    if len(nodes) == 0:
        return []
    else:
        d = cdist([node], nodes)[0]
        return list((_node, _d) for _node, _d in zip(nodes, d) if _d <= threshold)


targetdirs = sys.argv[1:]
frame = 20

# os.makedirs(f'{targetdir}/lastflow',exist_ok=True)
from collections import deque
import time

model.detect([np.zeros((1, 1, 3), dtype=np.uint8)], verbose=0)
if 0:
    plc = readplc()
    SIDE = plc.SIDE
    SIZE = plc.size
    if SIZE >= 40:
        SIZEX = '4x'
    else:
        SIZEX = '20'
    camnames = [f't{SIDE}{SIZEX}f', f't{SIDE}{SIZEX}b']
    cam = dict()
    for camname in camnames:
        cam[camname] = sa.attach(f'shm://{camname}_raw')
    while True:
        plc = readplc()

for targetdir in targetdirs:
    os.makedirs(f'{targetdir}/flow4c', exist_ok=True)
    os.makedirs(f'{targetdir}/maskc', exist_ok=True)
    if len(glob.glob(f'{targetdir}/flow4c/*.jpg')) > 0:
        #continue
        pass
    for bf in 'bf':
        image0 = None
        newmask0 = None
        linktoorigin = dict()
        lastlinktoorigin = dict()
        sift0 = None
        for i, f in enumerate(sorted(glob.glob(f'{targetdir}/{bf}*.jpg'))[:frame + 1]):
            # for f in [sorted(glob.glob(f'{targetdir}/{bf}*.jpg'))[0],sorted(glob.glob(f'{targetdir}/{bf}*.jpg'))[frame]]:
            start = time.time()
            basef = os.path.basename(f)
            image = cv2.imread(f)[:, :, ::-1]
            newmask = maskoutcontainer(image, False, maskfile=f'{targetdir}/maskc/{basef}')
            print("Tmaskoutcontainer:", time.time() - start)
            if image0 is not None:
                out, kpxy, sift0 = bsmatcher(image0, image, newmask0, newmask, sift0=sift0)
                print("Tbsmatcher:", time.time() - start)
                out2 = None
                if 1:
                    plt.cla()
                    ax = plt.gca()
                    plt.imshow(image)
                    x1 = []
                    y1 = []
                    x2 = []
                    y2 = []
                    ds=[]
                    for k1,k2 in out:
                        x1.append(k1[0])
                        y1.append(k1[1])
                        x2.append(k2[0])
                        y2.append(k2[1])
                        ds.append(y2[-1] - y1[-1])

                    data = []
                    for _x1, _y1, _x2, _y2 in zip(x1, y1, x2, y2):
                        # circle1=plt.Circle((_x1,_y1),50,fill=False)
                        # circle2=plt.Circle((_x2,_y2),50,fill=False)
                        # ax.add_artist(circle1)
                        # ax.add_artist(circle2)
                        if _y2-_y1 <= -55:
                            data.append([_x1, _x2])
                            data.append([_y1, _y2])
                            data.append('r')
                        elif _y2-_y1 >= 40:
                            data.append([_x1, _x2])
                            data.append([_y1, _y2])
                            data.append('g')
                        else:
                            data.append([_x1, _x2])
                            data.append([_y1, _y2])
                            data.append('b')
                    print("Tdataappend:", time.time() - start)
                    plt.scatter(x1, y1)
                    plt.scatter(x2, y2)
                    plt.plot(*data)
                    plt.xlim(0, 1280)
                    plt.ylim(720, 0)
                    _3largest=heapq.nlargest(3,ds)
                    _3smallest=heapq.nsmallest(3,ds)
                    for i in range(3):
                        plt.text(0, 100 + i * 100, _3smallest[i], fontsize=16, fontweight='bold', color='red')
                        plt.text(0, 400+i*100, _3largest[2-i], fontsize=16, fontweight='bold', color='green')
                    print("Tplot:", time.time() - start)
                    plt.savefig(f'{targetdir}/flow4c/{basef}')
                    print("Tsavefig:", time.time() - start)
            else:
                plt.cla()
                ax = plt.gca()
                plt.imshow(image)
                plt.savefig(f'{targetdir}/flow4c/{basef}')

            if image0 is None:
                image0 = image
                newmask0 = newmask
