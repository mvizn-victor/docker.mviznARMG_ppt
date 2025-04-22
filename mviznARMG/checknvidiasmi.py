#version:1
import os
import time
T=time.time()
os.system('nvidia-smi >/dev/null')
print('nvidia-smi takes',time.time()-T)
if (time.time()-T)>1:
    os.system('date >> /opt/captures/restart.txt')
    os.system('reboot')

