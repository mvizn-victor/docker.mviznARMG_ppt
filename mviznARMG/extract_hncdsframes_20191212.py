from config.config import *
from yolohelper import detect as YOLO
from yolohelper import detect2 as YOLO2
import shutil
import glob
#os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211',exist_ok=True)
#os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211.done',exist_ok=True)
os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191212',exist_ok=True)
import re
if 1:
    flist=glob.glob('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/*/*/*.jpg')
    print(len(flist))
    i=0
    for f in sorted(flist):
        i=i+1
        print(i)
        if i<31817:continue
        try:
            DATE,TIME,CAM=re.match('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/([^/]*)/[^/]*/([^_]*)_([^_]*)_[^_]*.jpg',f).groups()
        except:
            DATE, TIME, CAM = re.match('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/[^/]*/[^/]*/([^_]*)_([^_]*)_([^_]*)_[^_]*.jpg', f).groups()
        #if DATE in ['2019-11-27','2019-11-28']:continue
        frame=cv2.imread(f)
        if  frame is None or min(frame.shape[:2])==0:
            continue
        if CAM in ['ovls','ovss','pmnls','pmnss','ovtrls','ovtrss']:
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDS.cfg",
                                    weightPath="HNCDS/weights/HNCDS.weights",
                                    metaPath="HNCDS/weights/HNCDS.data")
            results=list(x for x in results if x[0]!='t')
        else:
            results = YOLO2.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDSside.cfg",
                                    weightPath="HNCDS/weights/HNCDSside.weights",
                                    metaPath="HNCDS/weights/HNCDSside.data")
        if len(results)>0:
            shutil.copy(f, f'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191212/{DATE}_{TIME}_{CAM}_0.jpg')
            print(f,'yes')
        else:
            print(f, 'no')

if 0:
    for f in sorted(glob.glob('/tmp/tmp/*')):
        bname = os.path.basename(f)
        camname=bname.split('_')[2]
        #donefile=f'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211.done/{bname}.done'
        #if os.path.exists(donefile):
        #    continue
        frame=cv2.imread(f)
        if camname in ['ovls','ovss','pmnls','pmnss','ovtrls','ovtrss']:
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDS.cfg",
                                    weightPath="HNCDS/weights/HNCDS.weights",
                                    metaPath="HNCDS/weights/HNCDS.data")
            results=list(x for x in results if x[0]!='t')
        else:
            results = YOLO2.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDSside.cfg",
                                    weightPath="HNCDS/weights/HNCDSside.weights",
                                    metaPath="HNCDS/weights/HNCDSside.data")
        if len(results)>0:
            shutil.copy(f,'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211')
            print(f,'yes')
        else:
            print(f, 'no')
        #open(donefile,'w')