from config.config import *
from yolohelper import detect as YOLO
from yolohelper import detect2 as YOLO2
import shutil
import glob
#os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211',exist_ok=True)
#os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191211.done',exist_ok=True)
os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191214',exist_ok=True)
os.makedirs('/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191214_no',exist_ok=True)
import re
if 1:
    flist=glob.glob('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/*/*/*.jpg')
    print(len(flist))
    i=0
    for f in sorted(flist):
        i=i+1
        print(i)
        #if i<31817:continue
        try:
            DATE,TIME,CAM=re.match('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/([^/]*)/[^/]*/([^_]*)_([^_]*)_[^_]*.jpg',f).groups()
        except:
            DATE, TIME, CAM = re.match('/mnt/NFSDIR/ARMG-Project-Data/captures/7409/captures/HNCDS/photologs_raw/[^/]*/[^/]*/([^_]*)_([^_]*)_([^_]*)_[^_]*.jpg', f).groups()
        #if DATE in ['2019-11-27','2019-11-28']:continue
        if DATE<'2019-12-12':continue
        frame=cv2.imread(f)
        if  frame is None or min(frame.shape[:2])==0:
            continue
        if CAM in ['ovls','ovss','pmnls','pmnss']:
            results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDS.cfg",
                                    weightPath="HNCDS/weights/HNCDS.weights",
                                    metaPath="HNCDS/weights/HNCDS.data")

        else:
            results = YOLO2.inferImg(np_image=frame, thresh=0.2,
                                    configPath="HNCDS/weights/HNCDSside.cfg",
                                    weightPath="HNCDS/weights/HNCDSside.weights",
                                    metaPath="HNCDS/weights/HNCDSside.data")
        results2=list(x for x in results if x[0]!='t')                                            
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            prob = result[1]
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = int(result[2][3] / 2)
            boxw = int(result[2][2] / 2)
            SIZE = max(boxw, boxh) * 2
            x1 = xc - boxw
            y1 = yc - boxh
            x2 = xc + boxw
            y2 = yc + boxh
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
            cv2.putText(frame, f'{name}', (xc - 15, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 1)

        if len(results2)>0:
            cv2.imwrite(f'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191214/{DATE}_{TIME}_{CAM}_0.jpg',frame)
            print(f,'yes')
        elif len(results)>0:
            cv2.imwrite(f'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191214_no/{DATE}_{TIME}_{CAM}_no.jpg',frame)
            print(f,'truckonly')        
        else:
            shutil.copy(f, f'/mnt/NFSDIR/ARMG-Project-Data/HNCDS/hits_20191214_no/{DATE}_{TIME}_{CAM}_0.jpg')
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
