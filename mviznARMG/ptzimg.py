import os
os.system('rm -rf /dev/shm/ptzimg')
#os.chdir('/home/mvizn/Code/mviznARMG')
from config.config import *
os.makedirs('/dev/shm/ptzimg/',exist_ok=True)
for ls,fbc in ['lf','lb','lc','sf','sb','sc']:
    camname=f'cn{ls}sb{fbc}'
    cam=eval(camname)
    configf=f'config/tcds/{camname}20.txt'
    cam.loadpostxt(configf)
for ls in ['l','s']:
    camname=f'ov{ls}s'
    cam=eval(camname)
    configf=f'config/pmnrs/{camname}.txt'
    cam.loadpostxt(configf)
time.sleep(2)
for ls,fbc in ['lf','lb','lc','sf','sb','sc']:
    camname=f'cn{ls}sb{fbc}'
    cam=eval(camname)
    cam.snapshot(f'/dev/shm/ptzimg/{camname}.jpg')
for ls in ['l','s']:
    camname=f'ov{ls}s'
    cam=eval(camname)
    cam.snapshot(f'/dev/shm/ptzimg/{camname}.jpg')
list_camname=list(f't{ls}{sz}{fb}' for ls in ['l','s'] for sz in ['20','4x'] for fb in ['f','b'])
for camname in list_camname:
    cam=eval(camname)
    cam.snapshot(f'/dev/shm/ptzimg/{camname}.jpg')
time.sleep(2)
