#version:1
from config.config import *
import glob
w,h=int(sys.argv[1]),int(sys.argv[2])
shms=[]
for x in sys.argv[3:]:
    for shmfile in sorted(glob.glob(f'/dev/shm/*{x}*')):
        fbasename=os.path.basename(shmfile)
        shm=sa.attach(f'shm://{fbasename}')
        shms.append((os.path.basename(shmfile),shm))

n=len(shms)
import math
cols = int(math.ceil(n ** 0.5))
rows = int(math.ceil(n / cols))
w1=w//cols
h1=h//rows
print(w1,h1)
for i,(camname,shm) in enumerate(shms):
    row=i//cols
    col=i%cols
    cv2.namedWindow(camname)
    cv2.moveWindow(camname, col * w1, row*h1)
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
