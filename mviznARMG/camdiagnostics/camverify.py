#version:1
from config.config import *
from Utils.helper import *
import os
camverifydir='/opt/captures/camverify'
os.makedirs(camverifydir,exist_ok=True)
os.system(f'rm {camverifydir}/*')
if 1:
    for camname in ['cnlsbf','cnlsbb','cnlsbc','cnssbf','cnssbb','cnssbc']:   
        print(camname)
        cam=eval(camname)
        postxt=f'config/tcds/{camname}20.txt'
        cam.loadpostxt(postxt)
        while not cam.atpostxt(postxt):
            time.sleep(0.1)
        cam.snapshot(f'{camverifydir}/{camname}.jpg')
    for camname in ['ovls','ovss']:
        print(camname)
        cam=eval(camname)
        postxt=f'config/pmnrs/{camname}.txt'
        cam.loadpostxt(postxt)
        while not cam.atpostxt(postxt):
            time.sleep(0.1)
        cam.snapshot(f'{camverifydir}/{camname}.jpg')
    time.sleep(3)
quit()

print('pos1')
if 1:
    cam=cnlsbf
    postxt=f'config/tcds/cnlsbf45-1.txt'
    cam.loadpostxt(postxt)
    T=time.time()
    while True:
        if cam.atpostxt(postxt):break
        time.sleep(0.1)
        cam.positiontxt()
        time.sleep(0.1)        
        print(time.time()-T)
        
    print(time.time()-T)
print('pos2')
if 1:
    cam=cnlsbf
    postxt=f'config/tcds/cnlsbf45-2.txt'
    cam.loadpostxt(postxt)
    T=time.time()
    while True:
        if cam.atpostxt(postxt):break
        time.sleep(0.1)
        cam.positiontxt()
        time.sleep(0.1)
        print(time.time()-T)
    print(time.time()-T)
