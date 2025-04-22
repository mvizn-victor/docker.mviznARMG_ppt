from yolohelper import detect as YOLO
#from memcachehelper import memcacheRW as mcrw
import cv2
from time import time, process_time

#input_video = "/media/mvizn/8eb20be2-7812-4cf5-90ba-ab895b0b862f/Test-Videos/PSA-RTG/Demo/front-people.mp4"
#input_video = "/home/mvizn/Desktop/front-people.mp4"
#input_video = "/mnt/908b5279-0ff3-48ce-83be-f0f3a7d2926d/PSA-RawVideos/RTG1/2018-03-24/cam1-19_20.mp4"
input_video = "/mnt/NFSDIR/RawVideos/QC/QC924_NewCams/2020-02-25/qc924_cam1_2020-02-25_07-45.mp4"
camid = 'cam1'
render = True

#out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (540, 960))

cap = cv2.VideoCapture(input_video)
ret = True
framenum = 0
def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)
import glob   
for f in natural_sort(glob.glob('/home/mvizn/raid/rtg-train-uploads/d768b33d-51e9-4386-a944-c2afbf6be7ee/model_fcb98de2-e178-4462-9974-49a86b6acefe/imgs/*.jpg'))[::-1]:
    # Capture frame-by-frame
    #ret, frame = cap.read()
    ret=1
    frame=cv2.flip(cv2.imread(f),1)
    #frame=cv2.rotate(frame,cv2.ROTATE_180)
    if framenum % 1 == 0 and ret:
        #frame = cv2.resize(frame, (720, 1280))
        #cv2.imwrite('/tmp/%d.jpg'%framenum,frame)
        results = YOLO.inferImg(np_image=frame, thresh=0.2,
                                configPath="HNCDS/weights/HNCDSside.cfg",
                                weightPath="HNCDS/weights/HNCDSside.weights",
                               metaPath="HNCDS/weights/HNCDSside.data")
        #configPath = "/home/mvizn/raid/S3dstore/darknet-alexey-train/PSA-RTG-FB-WPT/yolov3_640x320.cfg",
        #weightPath = "/home/mvizn/raid/S3dstore/darknet-alexey-train/PSA-RTG-FB-WPT/backup/yolov3_640x320_4000.weights",
        #metaPath = "/home/mvizn/raid/S3dstore/darknet-alexey-train/PSA-RTG-FB-WPT/PSA_mvizn-demobox-2.data")

        t1 = time()
        #mcrw.write(camid=camid, tstamp=time(), results=results)
        #print("MC write took:", (time()-t1)*1000, 'ms')
        for result in sorted(results, key=lambda x: -x[1]):
            print(result[0], result[1])
        #input()
        if render:
            for result in sorted(results,key=lambda x:-x[1]):
                print(result[0],result[1])
            #input()
            for result in results:
                name = result[0]
                if type(name) == bytes:
                    name = name.decode('utf8')
                prob = result[1]
                xc = int(result[2][0])
                yc = int(result[2][1])
                boxh = int(result[2][3] / 2)
                boxw = int(result[2][2] / 2)

                x1 = xc - boxw
                y1 = yc - boxh
                x2 = xc + boxw
                y2 = yc + boxh

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 4)
                cv2.putText(frame, name, (xc, yc), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
            #cv2.imshow("out", cv2.resize(frame, (540, 960)))
            cv2.imshow("out", frame)
            #out.write(cv2.resize(frame, (540, 960)))
            if len(results)>1:
                cv2.waitKey(0)
            else:
                cv2.waitKey(1)
            #cv2.imwrite('/tmp/test/out2/%d.jpg' % framenum, frame)
    framenum += 1

# When everything done, release the capture
cap.release()
#out.release()
cv2.destroyAllWindows()

