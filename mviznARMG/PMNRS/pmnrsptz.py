#version:gd28
#gd28
#tilt front for dst 20ft rear
from config.config import *
from Utils.helper import *
from memcachehelper import memcacheRW as mcrw
import time
lastJA=0
STATE='HOME'
CanMoveCam=False
lastCanMoveCam=False
PMNRS_COMPLETED=False
plc = readplc()
SIDE=plc.SIDE
if plc.ppm:
    print(f'PPM pan once')
while True:
    T1 = time.time()
    plc=readplc()
    if not plc.JA:break
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)-mcrw.raw_read('Tjobstart',0)>0
    if pmnumber_match and not PMNRS_COMPLETED:
        print(f'PMNRS_COMPLETED due to match')
        PMNRS_COMPLETED=True
        mcrw.raw_write('PMNRS_COMPLETED', time.time())
    CanMoveCam=plc.JA and not plc.MI

    if SIDE in 'ls':
        camname=f'ov{SIDE}s'
        cam=eval(camname)
        if plc.JOBTYPE=='OFFLOADING' and plc.TLOCK and not PMNRS_COMPLETED:
            print('OFFLOADING and TLOCK -> PMNRS_COMPLETED')
            PMNRS_COMPLETED=True
            mcrw.raw_write('PMNRS_COMPLETED', time.time())
        elif plc.JOBTYPE=='MOUNTING' and plc.HoistPos<=8500 and plc.TrolleyPos==plc.SIDEINFO and not PMNRS_COMPLETED:
            print('MOUNTING and HOISTPOS TROLLEY POS met condition -> PMNRS_COMPLETED')
            PMNRS_COMPLETED=True
            mcrw.raw_write('PMNRS_COMPLETED', time.time())

        if PMNRS_COMPLETED and CanMoveCam and STATE!='HOME':
            #Only truly ends after camera moved to home position
            print(f'PMNRS COMPLETED:{STATE}->HOME')
            STATE='HOME'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=0,forcezoom=0)
            time.sleep(3) #panning is a thread operation need to wait for it to complete
            break
        if STATE=='HOME' and plc.ppm:
            mcrw.raw_write(f'{camname}_ptz', time.time())
            #gd28
            if plc.containerpos in [3,4] and plc.dst:
                print('DST 20ft rear tilt +9')
                cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=+9,forcezoom=0)
            else:
                cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=0,forcezoom=0)
            STATE='ZOOMOUT'
            print('HOME->ZOOMOUT')
        elif STATE=='HOME':
            mcrw.raw_write(f'{camname}_ptz', time.time())
            if plc.containerpos in [1,2]:
                cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=-6,forcezoom=500)
            elif plc.containerpos in [3,4]:
                cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=+9,forcezoom=500)
            else:
                cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=+9,forcezoom=500)
            STATE='ZOOMOUT'
            print('HOME->ZOOMOUT')
        if STATE=='ZOOMOUT':
            mcrw.raw_write(f'{camname}_ptz', time.time())

    lastJA=plc.JA
    lastCanMoveCam=CanMoveCam
    Telapse = time.time() - T1
    time.sleep(max(0.1 - Telapse, 0))
