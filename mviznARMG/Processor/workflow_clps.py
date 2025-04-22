from config.config import *
import os
import time
lastJA=False
os.system('gnome-terminal --title=tfserve -- bash -c "bash tfserve.sh;bash"')
os.system('gnome-terminal --title=plcclient -- bash -c "python Processor/plcclient.py;bash"')

while 1:
    plc = readplc()
    if not lastJA and plc.JA:
        #new job started
        if plc.JOBTYPE in ['MOUNTING','OFFLOADING']:
            mcrw.raw_write('Tjobstart',time.time())
            mcrw.raw_write('pmnumber_read', '')
            mcrw.raw_write('lpnumber_read', '')
            mcrw.raw_write('pmnumber_match', 0)
            for i in range(1,5):
                mcrw.raw_write(f'tcds_corner{i}', 0)
            NOW=datetime.now()
            DATE=NOW.strftime('%Y-%m-%d')
            TIME=NOW.strftime('%H-%M-%S')
            LOGFILENAME=f'/opt/captures/JOBINFO/{DATE}.txt'
            printandlog(f'{DATE}_{TIME}',plc.JOBTYPE,plc.SIDE,plc.size,plc.pmnumber,file=makedirsopen(LOGFILENAME,'a'),sep=",")            
            os.system(f'gnome-terminal --title=framesharer -- python Processor/framesharer.py {plc.SIDE}')
            os.system(f'gnome-terminal --title=PMNRStop -- bash -c "sleep 1;python PMNRS/pmnrstop.py;bash"')
            os.system(f'gnome-terminal --title=PMNRSside -- bash -c "sleep 1;python PMNRS/pmnrsside.py;bash"')
            os.system(f'gnome-terminal --title=PMNRSptz -- bash -c "sleep 1;python PMNRS/pmnrsptz.py;bash"')
            os.system(f'gnome-terminal --title=HNCDStop -- bash -c "sleep 1;python HNCDS/hncdstop.py;bash"')
            os.system(f'gnome-terminal --title=HNCDSside -- bash -c "sleep 1;python HNCDS/hncdsside.py;bash"')
            if plc.JOBTYPE=='OFFLOADING':
                if plc.ppm:
                    os.system('gnome-terminal --title=TCDSptz -- bash -c "sleep 1;python TCDS/tcdsptz.py;bash"')
                    os.system('gnome-terminal --title=TCDS -- bash -c "sleep 1;python TCDS/tcds.py;bash"')
                else:
                    os.system('gnome-terminal --title=CLPSptz -- bash -c "sleep 1;python CLPS/clpsptz.py;bash"')
                    os.system('gnome-terminal --title=CLPS -- bash -c "sleep 1;python CLPS/clpscapture.py;bash"')
            os.system('gnome-terminal --title=viewshm -- bash -c "sleep 5;python viewshm.py 1920 1080 clps;bash"')
    if lastJA and not plc.JA:
        #job ended
        os.system('bash endjob.sh')
    cv2.imshow('quitter',np.zeros((1000,1000,3),dtype=np.uint8))
    c=cv2.waitKey(1)
    if c==ord('q'):
        os.system('bash killall.sh')
        break
    lastJA=plc.JA
    time.sleep(0.5)
