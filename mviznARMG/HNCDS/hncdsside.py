#version:he06
#gd21-1FPS
#gh22
#  enablebit=stopprocessing
#  for each camera, maintain hitlist. if hitlist has 2 or more elements then update plc
#ha03
#  snapshot when at row 1 for seaside, row 10 for landside
#he06
#  only send and record first moving image to CIU 
from shapely.geometry import Polygon, box, Point

def print(*x,**kw):
    from datetime import datetime
    if 'file' not in kw:
        DT=datetime.now()
        x=(DT,)+x
    __builtins__.print(*x,**kw)

from armgws.armgws import sendjson
from collections import defaultdict
import platform
deploy=platform.node() not in ['mvizn-demobox-2']
reported=defaultdict(int)

from yolohelper import detect as YOLO
from config.config import *
from Utils.helper import procimage
import json
dict__roi=json.loads(open('HNCDS/roi.json').read())

def mapinnerouterline(jobside,camname,trolleyposmm):
    '''
    pixelY   trolleyposmm    
    OVTRLS at LS
    -50 outer line
    290 center of truck 36259
    500 inner line
    719 trolleypos      28775
    OVTRSS at SS
    0   outer line
    322 center of truck -4314
    542 inner line
    719 trolleypos      2704    
    '''
    if jobside=='l':
        line=np.poly1d(np.polyfit([28775,36259],[719,290],1))        
        pixelshift=int(line(trolleyposmm)-line(28775))
        if camname=='ovtrls':                        
            innerline=500-pixelshift
            outerline=-50-pixelshift
        elif camname=='ovtrss':
            innerline=(720-500)+720+pixelshift-100
            outerline=(720--50)+720+pixelshift
    elif jobside=='s':
        line=np.poly1d(np.polyfit([2704,-4314],[719,322],1))
        pixelshift=int(line(trolleyposmm)-line(2704))
        if camname=='ovtrss':
            innerline=542-pixelshift
            outerline=0-pixelshift
        elif camname=='ovtrls':
            innerline=(720-542)+720+pixelshift-100
            outerline=(720-0)+720+pixelshift
    innerline=int(innerline)
    outerline=int(outerline)
    #print(innerline,outerline)
    return(innerline,outerline)

if deploy:
    plc=readplc()
    SIDE=plc.SIDE
    camraw = dict()
    camnames= [f't{SIDE}4xf',f't{SIDE}20f',f't{SIDE}20b',f't{SIDE}4xb',f'cn{SIDE}sbf',f'cn{SIDE}sbb','ovtrls','ovtrss']
    for camname in camnames:
        camraw[camname] = sa.attach(f"shm://{camname}_raw")
    if plc.JOBTYPE=='MOUNTING':
        _mt1ot2o='m'
    else:
        if plc.containerpos%2==0:
            _mt1ot2o='t2o'
        else:
            _mt1ot2o='t1o'
    if plc.size>=40:
        sizetype='4x'
    else:
        sizetype='20'        
else:
    camnames=['test']
    camraw = dict()
    #camraw['test']=cv2.imread('/home/mvizn/raid/rtg-train-uploads/d768b33d-51e9-4386-a944-c2afbf6be7ee/bf7eedf7-1b9f-4564-a662-590a92afbf32-304fc6fe-2447-4149-bbe1-eb5786505464/imgs/7109_2020-02-21_06-58-55_ts4xf_p.jpg')
    import glob
    imgs=glob.glob(
        '/home/mvizn/raid/rtg-train-uploads/d768b33d-51e9-4386-a944-c2afbf6be7ee/bf7eedf7-1b9f-4564-a662-590a92afbf32-304fc6fe-2447-4149-bbe1-eb5786505464/imgs/*.jpg'
    )
    import random
    camraw['test']=cv2.imread(random.choice(imgs))

#ha03
class C__risechecker:
    def __init__(self):
        self.curr=False
        self.last=False
    def update(self,cond):
        self.curr=cond
        ret = self.curr and not self.last
        self.last=self.curr
        return ret
d__risechecker={}
for camname in camnames:
    d__risechecker[camname]=C__risechecker()

polygons=dict()
for camname in camnames:
    polygons[camname]=[]
    try:
        if 'cn' not in camname:
            #ignore cn text files in config
            x1,y1,x2,y2,x3,y3,x4,y4=map(int,open(f'/home/mvizn/Code/mviznARMG/config/hncds/{camname}.txt').read().strip().split())
            polygon=[(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
            polygons[camname].append(polygon)
    except:
        pass
    roikey=f'{camname}_{sizetype}_{_mt1ot2o}'
    if roikey in dict__roi:
        polygons[camname].append(dict__roi[roikey])
imshow=dict()
os.system('rm /dev/shm/*_hncdsside')
for camname in camnames:
    imshow[camname]=createShm(f'{camname}_hncdsside')

##begin gh22 1##
def updateandqueryhitlist(camname,x,y):
    found=0
    for x1,y1 in hitlist[camname]:
        if ((x1-x)**2+(y1-y)**2)**.5<hitlistd:
            found=1
    if not found:
        hitlist[camname].append((x,y))
    return len(hitlist[camname])
hitlist=dict()
hitlistd=50
for camname in camnames:
    hitlist[camname]=[]
##end gh22 1##

Tjobstart=datetime.fromtimestamp(mcrw.raw_read('Tjobstart',0))
JOBDATE=Tjobstart.strftime("%Y-%m-%d")
JOBTIME=Tjobstart.strftime("%H-%M-%S")
INCEPTIONDIRNAME=f'/opt/captures/HNCDS/photologs_raw/{JOBDATE}/inception'
PHOTOLOGDIRNAME=f'/opt/captures/HNCDS/photologs/{JOBDATE}/{JOBTIME}'
PHOTOLOGRAWDIRNAME=f'/opt/captures/HNCDS/photologs_raw/{JOBDATE}/{JOBTIME}'
LOGFILENAME=f'/opt/captures/HNCDS/logs/{JOBDATE}.txt'

lastT1 = 0
detectiongrid=dict()
ignoretime=0
for camname in camnames:
    detectiongrid[camname]=np.zeros((73,129),dtype=np.int)
lastHNCDS_OpsAck = 0
while True:
    T=time.time()
    NOW = datetime.fromtimestamp(time.time()//1*1)
    DATE = NOW.strftime('%Y-%m-%d')
    TIME = NOW.strftime('%H-%M-%S')
    while True:
        if not deploy:break
        mcrw.raw_write('hncdsside_active', time.time())
        plc = readplc()
        if plc.GantryCurrSlot==plc.GantryTargetSlot:
            break
        print('waiting for GantryCurrSlot==GantryTargetSlot')            
        time.sleep(0.5)


    print(datetime.now(),"bytes78",bin(plc.data[78]))
    HNCDS_StopProcessing = plc.HNCDS_Enable #repurposed
    if HNCDS_StopProcessing:
        mcrw.raw_write('hncds_processing',0)
        mcrw.raw_write('hncdsside_active',time.time())
        time.sleep(0.25)
        continue
    else:
        mcrw.raw_write('hncds_processing',time.time())
    for camname in camnames:
        hasmoving=0 #gh22 4
        mcrw.raw_write('hncdsside_active', time.time())
        va = 0
        vh = 0
        vp = 0    
        frame = camraw[camname].copy()
        frame_cpy = frame.copy()
        if 'ovtr' in camname:
            if abs(plc.TrolleyPos-plc.SIDEINFO)>1:
                #ignore ovtr cameras when trolley not in position
                continue
            innerline,outerline=mapinnerouterline(SIDE,camname,plc.TrolleyPosCurrMM)
            roi=box(0,innerline,1280,outerline)
            cv2.line(frame_cpy,(0,innerline),(1280,innerline),(0,255,0),3)
            cv2.line(frame_cpy,(0,outerline),(1280,outerline),(0,255,0),3)
        results = procimage('hncdssideyolo',frame)
        for polygon in polygons[camname]:
            if 'cn' in camname:
                #polygon for cn cam is inclusion
                cv2.polylines(frame_cpy,[np.array(polygon).reshape((-1,1,2))],3,(0,255,0)) 
            else:
                #polygon for tx cam is exclusion
                cv2.line(frame_cpy, (polygon[0][0],polygon[0][1]),(polygon[-1][0],polygon[-1][1]),(0,255,0), 3)

        windows=[]
        for result in results:
            name = result[0]
            if type(name) == bytes:
                name = name.decode('utf8')
            if name not in ['w','s','x']: continue
            prob = result[1]
            xc = int(result[2][0])
            yc = int(result[2][1])
            boxh = int(result[2][3] / 2)
            boxw = int(result[2][2] / 2)
            x1 = xc - boxw
            y1 = yc - boxh
            x2 = xc + boxw
            y2 = yc + boxh
            windows.append(box(x1,y1,x2,y2))

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
            #if name == 'p' and camname not in ['ovls','ovss']:
            if name == 'p':
                #ignore static object detected before
                if detectiongrid[camname][yc//10,xc//10]==0:
                    detectiongrid[camname][yc//10,xc//10]=int(time.time())
                if detectiongrid[camname][yc//10,xc//10]<ignoretime:
                    print(camname,xc,yc,'ignore due to opsack')
                    continue
            excluded = 0
            BOX=box(x1,y1,x2,y2)            
            for window in windows:
                #driver in cabin
                if box(x1,y1,x2,y2)&window:
                    excluded=1
                    break
            for polygon in polygons[camname]:
                #in txcamera opposite lane
                POLYGON=Polygon(polygon)
                
                if 'cn' in camname:
                    try:
                        if (BOX&POLYGON).area/BOX.area<0.5:
                            excluded=1
                    except:
                        print(camname)
                        print('BOX',BOX)
                        print('POLYGON',POLYGON)
                else:
                    if (BOX&POLYGON).area/BOX.area>0.5:
                        excluded=1
                
            if 'ovtr' in camname:
                POLYGON=roi
                if (BOX&POLYGON).area/BOX.area<0.5:
                    excluded=1
            if excluded:
                pass
                continue
            if name=='w' or name=='s' or name=='x':
                color = (0,255,0)
            if 1:
                if name == 'p' and prob<0.3:
                    continue
                if name == 'p':
                    makedirsimwrite(f'{INCEPTIONDIRNAME}/{DATE}_{TIME}_{camname}.jpg', frame[max(0, y1):y2, max(0, x1):x2])
                if name == 'p' and procimage('hncdsinception',frame[max(0,y1):y2,max(0,x1):x2])[0]!='p':
                    continue
                if name == 'p':
                    color = (0, 0, 255)
                    vp = 1
                    ##begin gh22 2##
                    hitcount=updateandqueryhitlist(camname,xc,yc)
                    if hitcount>=2:
                        mcrw.raw_write('last_hncds_p', time.time())
                        hasmoving=1
                    ##end gh22 2##
            cv2.rectangle(frame_cpy, (x1, y1), (x2, y2), color, 4)
            cv2.putText(frame_cpy, f'{name}:{prob:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (255, 0, 0), 2)
        violations = vp * 'p' + va * 'a' + vh * 'h'
        if deploy and len(violations) > 0:
            ##begin gh22 3
            makedirsimwrite(f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame_cpy)
            if not reported[DATE,TIME,camname,violations] and hasmoving and 'p' in violations:
                makedirsimwrite(f'{PHOTOLOGDIRNAME}/moving/{DATE}_{TIME}_{camname}_{violations}.jpg', frame_cpy)
                sendjson('HNCDS',camname.upper(),NOW,plc,f'{PHOTOLOGDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg')
                reported[DATE,TIME,camname,violations]=1
            makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/{DATE}_{TIME}_{camname}_{violations}.jpg', frame)
            ##end gh22 3

            printandlog(f'{JOBDATE}_{JOBTIME}', f'{DATE}_{TIME}', camname, violations, file=makedirsopen(LOGFILENAME, 'a'), sep=",")
        #ha03
        snapshotcond=d__risechecker[camname].update(abs(plc.TrolleyPos-plc.SIDEINFO)<=1)
        print(camname,('plc.TrolleyPos','plc.SIDEINFO'),'=',(plc.TrolleyPos,plc.SIDEINFO),snapshotcond)
        if snapshotcond:
            print(camname,'snapshot!')
            makedirsimwrite(f'{PHOTOLOGDIRNAME}/snapshot/{DATE}_{TIME}_{camname}.jpg', frame_cpy)
            makedirsimwrite(f'{PHOTOLOGRAWDIRNAME}/snapshot/{DATE}_{TIME}_{camname}.jpg', frame)

        assignimage(imshow[camname], frame_cpy)
        if not deploy:
            cv2.imshow('',imshow[camname])
            cv2.waitKey(1)
            camraw['test'] = cv2.flip(cv2.imread(random.choice(imgs)),1)
    Telapse=time.time()-T
    print(Telapse)
    #time.sleep(max(0.5-Telapse,0))
    time.sleep(max(0.95-Telapse,0))

mcrw.raw_write('hncds_processing',0)
