from config.config import *
from Utils.helper import *
from memcachehelper import memcacheRW as mcrw
import time
lastJA=0
STATE='HOME'
CanMoveCam=False
lastCanMoveCam=False
PMNRS_SUCCESS=False
PMNRS_COMPLETED=False
while True:
    T1 = time.time()
        
    plc=readplc()
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)
    if pmnumber_match and not PMNRS_COMPLETED:
        print(f'PMNRS_COMPLETED due to match')    
        PMNRS_COMPLETED=True
    SIDE='l'#plc.SIDE
    CanMoveCam=1#plc.JA and not plc.MI# and not plc.externalpm #currently disable panning for external pm
    if plc.JA and not lastJA:
        print(f'Job started')    
        #job just started
        PMNRS_COMPLETED=False
        if not plc.externalpm and plc.size==40 or plc.size==45:
            print(f'PPM 40,45 dont move camera')
            CanMoveCam=False
            
    if lastCanMoveCam and not CanMoveCam:
        print(f'MI:{plc.MI} JA:{plc.JA} aborted:{STATE}->HOME')
        STATE='HOME'
    if SIDE in 'ls':
        camname=f'ov{SIDE}s'
        cam=eval(camname)
        if plc.JOBTYPE=='OFFLOADING' and plc.TLOCK and not PMNRS_COMPLETED:
            print('OFFLOADING and TLOCK -> PMNRS_COMPLETED')
            PMNRS_COMPLETED=True            
        elif plc.JOBTYPE=='MOUNTING' and plc.HoistPos<=8500 and plc.TrolleyPos==plc.SIDEINFO and not PMNRS_COMPLETED:
            print('MOUNTING and HOISTPOS TROLLEY POS met condition -> PMNRS_COMPLETED')        
            PMNRS_COMPLETED=True
                                    
        if PMNRS_COMPLETED and CanMoveCam and STATE!='HOME':
            print(f'PMNRS COMPLETED:{STATE}->HOME')
            STATE='HOME'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=0,forcezoom=0)

        if STATE=='HOME':
            print('HOME->PLUS1')
            STATE='PLUS1'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=6)
            Tcam=time.time()
            cam.snapshot(f'/tmp/{STATE}.jpg',0.5)
        elif STATE=='PLUS1' and time.time()-Tcam>=3:
            print('PLUS1->PLUS2')
            STATE='PLUS2'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=12)
            Tcam = time.time()
            cam.snapshot(f'/tmp/{STATE}.jpg',0.5)
        elif STATE=='PLUS2' and time.time()-Tcam>=3:
            print('PLUS2->MINUS1')
            STATE='MINUS1'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt', tiltoffset=-6)
            Tcam = time.time()
            cam.snapshot(f'/tmp/{STATE}.jpg',0.5)
        elif STATE=='MINUS1' and time.time()-Tcam>=3:
            print('MINUS1->PLUS1')
            STATE='PLUS1'
            cam.loadpostxt(f'config/pmnrs/{camname}.txt',tiltoffset=6)
            Tcam = time.time()
            cam.snapshot(f'/tmp/{STATE}.jpg',0.5)

    lastJA=plc.JA
    lastCanMoveCam=CanMoveCam
    Telapse = time.time() - T1
    time.sleep(max(0.1 - Telapse, 0))
