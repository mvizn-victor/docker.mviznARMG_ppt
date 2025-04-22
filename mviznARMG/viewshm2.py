#version:1
from config.config import *
import glob
w,h,x0,y0=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
shms=[]
for x in sys.argv[5:]:
    for shmfile in sorted(glob.glob(f'/dev/shm/*{x}*')):
        if 'yolo' in shmfile or 'inception' in shmfile:
            continue
        fbasename=os.path.basename(shmfile)
        print(fbasename)
        shm=sa.attach(f'shm://{fbasename}')
        shms.append((os.path.basename(shmfile),shm))

n=len(shms)
import math
cols = int(math.ceil(n ** 0.5))
rows = int(math.ceil(n / cols))
w1=(w-x0)//cols
h1=(h-y0*(rows+1))//rows
for i,(camname,shm) in enumerate(shms):
    row=i//cols
    col=i%cols
    cv2.namedWindow(camname)
    cv2.moveWindow(camname, x0+col * w1, y0+row*(h1+y0))
while True:
    T=time.time()
    for (camname,shm) in shms:
        shm=sa.attach(f'shm://{camname}')
        cv2.imshow(camname,scaleimage(shm,w1,h1))
        c=cv2.waitKey(1)
        if c==ord('q'):
            raise
    Telapse=time.time()-T
    print(Telapse)
    time.sleep(max(0.05-Telapse,0))
