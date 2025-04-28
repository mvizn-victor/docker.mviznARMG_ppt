#version:1
from config.config import *
import glob
import math
from vcutils.helperfun import *
from vcutils.C__flaskdisplay import *
d__fd={}
d__fd['tcds']=C__flaskdisplay('TCDS')
d__fd['pmnrs']=C__flaskdisplay('PMNRS')
d__fd['hncds']=C__flaskdisplay('HNCDS')
d__fd['clps']=C__flaskdisplay('CLPS')
d__fd['main']=C__flaskdisplay('main')

print('sys.argv[5:]',sys.argv[5:])

fd=C__flaskdisplay('main')
d__shms={}
for groupname in d__fd:
    shms=[]
    if groupname=='main':
        for x in sys.argv[5:]:
            for shmfile in sorted(glob.glob(f'/dev/shm/*{x}*')):
                if 'yolo' in shmfile or 'inception' in shmfile:
                    continue
                fbasename=os.path.basename(shmfile)
                print(groupname,fbasename)
                shm=sa.attach(f'shm://{fbasename}')
                shms.append((os.path.basename(shmfile),shm))
    else:
        for x in ['_'+groupname]:
            for shmfile in sorted(glob.glob(f'/dev/shm/*{x}*')):
                if 'yolo' in shmfile or 'inception' in shmfile:
                    continue
                fbasename=os.path.basename(shmfile)
                print(groupname,fbasename)
                shm=sa.attach(f'shm://{fbasename}')
                shms.append((os.path.basename(shmfile),shm))
    d__shms[groupname]=shms
    print(groupname,len(d__shms[groupname]))

groupname='main'
while True:
    shms=d__shms[groupname]
    T=time.time()
    l__shm=[]
    if len(shms)>0:
        for (camname,shm) in shms:
            im1=sa.attach(f'shm://{camname}')
            imlabel=np.zeros((50,im1.shape[1],3),np.uint8)
            putText(imlabel,"\n"+camname,(0,0),font_scale=1.5,thickness=4)
            l__shm.append(vstack([im1,imlabel]))
        im=resizefit(gencollage(l__shm,cols=math.ceil(len(shms)**.5)))
        k=fd.imswk(im,1)
        if k==ord('m'):
            groupname='main'
        elif k==ord('h'):
            groupname='hncds'
        elif k==ord('t'):
            groupname='tcds'
        elif k==ord('c'):
            groupname='clps'
        elif k==ord('p'):
            groupname='pmnrs'
    else:
        im=np.zeros((1920,1080,3),np.uint8)
    Telapse=time.time()-T
    print(Telapse)
    time.sleep(max(0.2-Telapse,0))
