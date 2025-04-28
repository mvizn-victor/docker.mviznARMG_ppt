#version:id23
#ehz:
#  replace gnome-terminal with screen
#  disable quitter
#id23:
#  simulation2
import glob
from config.config import *
import os
from datetime import date,datetime
simulation = os.path.exists('/dev/shm/simARMG')
simulation2 = os.path.exists('/dev/shm/simARMG2')
while os.system('touch /opt/captures/test')!=0:    
    print('touch /opt/captures/test failed')
    time.sleep(0.5)
print(datetime.now(),file=open('/tmp/vastarttime.txt','w'))
lastJA=False
#os.system('screen -dSm restarter bash restarter.sh ')
os.system('rm /dev/shm/*/*.pkl')
os.system('rm /dev/shm/*/*.jpg')

from string import Template
template=Template('''
mkdir -p /opt/captures/screenlogs/$app
screen -dSm "$app" bash -c "
while true; do
    echo running $app
    export PYTHONPATH=.    
    stdbuf -oL python3 -u $script
    echo $app terminated
    echo rerun
    date
    sleep 1
done 2>&1 | tee -a /opt/captures/screenlogs/$app/log.txt
"''')

if not simulation:
    #os.system('screen -dSm tfserve bash -c "while true;do bash tfserve.sh;sleep 1;done;bash"')
    l__app__script=[]
    l__app__script.append(['hncdsinception','HNCDS/hncdsinception.py'])
    l__app__script.append(['hncdstopyolo','HNCDS/hncdstopyolo.py'])
    l__app__script.append(['hncdssideyolo','HNCDS/hncdssideyolo.py'])
    if not simulation2:
        l__app__script.append(['plcclient','Processor/plcclient.py'])
    else:     
        l__app__script.append(['plcclient','Processor/plcclient_sim.py'])

    for app,script in l__app__script:
        print(app,script)
        os.system(template.safe_substitute(app=app,script=script))
    #os.system('screen -dSm hncdsinception bash -c "while true;do python3 HNCDS/hncdsinception.py;sleep 1;done;echo hncdsinception;bash"')
    #os.system('screen -dSm pmnrstextboxdetector bash -c "while true;do python3 PMNRS/textboxdetector.py;sleep 1;done;echo textboxdetect;bash"')
    #os.system('screen -dSm hncdstopyolo bash -c "while true;do python3 HNCDS/hncdstopyolo.py;sleep 1;done;echo hncdstopyolo;bash"')
    #os.system('screen -dSm hncdssideyolo bash -c "while true;do python3 HNCDS/hncdssideyolo.py;sleep 1;done;echo hncdssideyolo;bash"')
    #os.system('screen -dSm psfaux bash -c "while true;do bash psfaux.sh;sleep 1;done;echo psfaux;bash"')
    #os.system('screen -dSm plcclient bash -c "while true;do python3 Processor/plcclient.py;sleep 1;done;echo plcclient;bash"')
else:
    os.system(template.safe_substitute(app=app,script=script))
    #os.system('screen -dSm plcclient bash -c "while true;do python3 Processor/plcclient.py;sleep 1;done;echo plcclient;bash"')
    pass

try:
    viewshm=sys.argv[1]
except:
    viewshm='_pmnrs'

viewshm='main'

MOUNTINGOFFLOADING=False
Tjobstart=0
Tlastlog=0
while 1:
    if simulation and not os.path.exists('/dev/shm/simARMG'):
        raise KeyboardInterrupt
    if simulation2 and not os.path.exists('/dev/shm/simARMG2'):
        raise KeyboardInterrupt
    plc = readplc()
    mcrw.raw_write('JA',plc.JA)
    NOW=datetime.now()
    DATE=NOW.strftime('%Y-%m-%d')
    TIME=NOW.strftime('%H-%M-%S')
    if time.time()-Tlastlog>.1 and time.time()-Tjobstart<10:
        timefrac=int(time.time()%1/0.1)
        Tlastlog=time.time()
        D=f'/opt/captures/psfaux/{DATE}/JOBSTART/{JOBDATE}_{JOBTIME}'
        os.makedirs(D,exist_ok=True)
        os.system(f'ps faux|gzip > {D}/{DATE}_{TIME}.{timefrac}_psfaux.txt.gz &')
        os.system(f'nvidia-smi > {D}/{DATE}_{TIME}.{timefrac}_nvidia-smi.txt &')
    if not plc.JA:
        mcrw.raw_write('pmnumber_read', '')
        mcrw.raw_write('lpnumber_read', '')
        mcrw.raw_write('pmnumber_match', 0)
        mcrw.raw_write('pmnumbers',set())
        for i in range(1,9):
            mcrw.raw_write(f'tcds_corner{i}', 0)
        mcrw.raw_write('tcds_cf',0)
        mcrw.raw_write('tcds_cb',0)
        mcrw.raw_write('tcds_cc',0)
        mcrw.raw_write('tcds_tf',0)
        mcrw.raw_write('tcds_tb',0)
        for i in range(1,9):
            mcrw.raw_write(f'tcds_corner{i}', 0)
        mcrw.raw_write(f'clps_liftdetected', 0)
        mcrw.raw_write(f'piggyback_liftdetected', 0)
        for i in range(1,5):
            mcrw.raw_write(f'clps_corner{i}', 0)
        for camname in ['ts20b', 'ts20f', 'tl20b', 'tl20f', 'ts4xb', 'ts4xf', 'tl4xb', 'tl4xf']:
            mcrw.raw_write(f'clps_moveoffdetected_{camname}', 0)

    if not lastJA and plc.JA:
        #new job started
        if plc.JOBTYPE in ['MOUNTING','OFFLOADING']:            
            JOBDATE=DATE
            JOBTIME=TIME
            Tjobstart=time.time()
            mcrw.raw_write('Tjobstart',NOW.timestamp())
            mcrw.raw_write('jobside',plc.SIDE)
            mcrw.raw_write('pmnumber_read', '')
            mcrw.raw_write('lpnumber_read', '')
            mcrw.raw_write('pmnumber_match', 0)
            mcrw.raw_write('pmnumbers',set())
            T1posaway=0
            T0posaway=0
            for i in range(1,9):
                mcrw.raw_write(f'tcds_corner{i}', 0)
            mcrw.raw_write('tcds_cf',0)
            mcrw.raw_write('tcds_cb',0)
            mcrw.raw_write('tcds_cc',0)
            mcrw.raw_write('tcds_tf',0)
            mcrw.raw_write('tcds_tb',0)

            LOGFILENAME=f'/opt/captures/JOBINFO/{DATE}.txt'
            printandlog(f'{DATE}_{TIME}',plc.JOBTYPE,plc.SIDE,plc.size,plc.pmnumber,file=makedirsopen(LOGFILENAME,'a'),sep=",")
            pmnumber=plc.pmnumber
            if not simulation:
                if not simulation2:
                    os.system(f'screen -dSm framesharer bash -c "unbuffer python3 Processor/framesharer.py {plc.SIDE};echo framesharer;bash" &')
                else:
                    os.system(f'screen -dSm framesharer bash -c "unbuffer python3 Processor/framesharer_sim.py {plc.SIDE};echo framesharer;bash" &')
            os.makedirs('/dev/shm/armglog',exist_ok=True)
            os.makedirs('/dev/shm/armglog.last', exist_ok=True)
            os.system('rm /dev/shm/armglog/*')
            def getteestr(title):
                return f'2>&1|cat > /dev/shm/armglog/{title}.log;touch /dev/shm/armglog/{title}.ended'
            if plc.pmnumber!='':
                title = 'PMNRStop'
                teestr = getteestr(title)
                os.system(f'bash -c "sleep 1;unbuffer python3 PMNRS/pmnrstop.py {teestr}" &')
                if len(glob.glob('/dev/shm/*_pmnrsside'))>0:
                    os.system('rm /dev/shm/*_pmnrsside')
                if not plc.ppm:
                    title = 'PMNRSside'
                    teestr = getteestr(title)
                    os.system(f'bash -c "sleep 1;unbuffer python3 PMNRS/pmnrsside.py {teestr}" &')
                title = 'PMNRSptz'
                teestr = getteestr(title)
                os.system(f'bash -c "sleep 1;unbuffer python3 PMNRS/pmnrsptz.py {teestr}" &')
            if 1:                
                title = 'HNCDStop'
                teestr = getteestr(title)
                os.system(f'bash -c "sleep 1;unbuffer python3 HNCDS/hncdstop.py {teestr}" &')
                title = 'HNCDSside'
                teestr = getteestr(title)
                os.system(f'bash -c "sleep 1;unbuffer python3 HNCDS/hncdsside.py {teestr}" &')
            viewshm2=viewshm
            if plc.JOBTYPE=='OFFLOADING':
                tcdsclps=''
                if plc.TCDS_Enable:
                    tcdsclps='TCDS'
                elif plc.CLPS_Enable:
                    tcdsclps='CLPS'
                else:
                    if plc.ppm:
                        tcdsclps='TCDS'
                    else:
                        tcdsclps='CLPS'
                if tcdsclps=='TCDS':
                    title = 'TCDSptz'
                    teestr = getteestr(title)
                    if simulation2:
                        os.system(f'bash -c "sleep 1;unbuffer python3 TCDS/tcdsptz_sim.py {teestr}" &')
                    else:
                        os.system(f'bash -c "sleep 1;unbuffer python3 TCDS/tcdsptz.py {teestr}" &')
                    title = 'TCDS'
                    teestr = getteestr(title)
                    os.system(f'bash -c "sleep 1;unbuffer python3 TCDS/tcds.py {teestr}" &')
                    if plc.containerpos in [2,4,6]:
                        title = 'piggyback'
                        teestr = getteestr(title)
                        os.system(f'bash -c "sleep 1;unbuffer python3 CLPS/piggyback.py {teestr}" &')
                    if viewshm=='main':
                        if plc.containerpos in [2,4,6]:
                            viewshm2='_piggyback'
                        else:
                            viewshm2='_tcds'
                elif tcdsclps=='CLPS':
                    title = 'CLPS_yolo'
                    teestr = getteestr(title)
                    os.system(f'bash -c "unbuffer python3 CLPS/clps_yolo.py {teestr}" &')
                    title = 'CLPSmrcnnloop'
                    teestr = getteestr(title)
                    os.system(f'bash -c "unbuffer python3 CLPS/clps_maskrcnn_loop.py {teestr}" &')
                    title = 'CLPSptz'
                    teestr = getteestr(title)
                    os.system(f'bash -c "sleep 1;unbuffer python3 CLPS/clpsptz.py {teestr}" &')
                    title = 'CLPS'
                    teestr = getteestr(title)
                    os.system(f'bash -c "sleep 1;unbuffer python3 CLPS/clps.py {teestr}" &')
                    if viewshm=='main':
                        viewshm2='_clps'
            else:
                if viewshm=='main':
                    viewshm2='_pmnrs'                
            #os.system(f'screen -dSm viewshm bash -c "sleep 5;unbuffer python3 viewshm2.py 1920 1080 100 50 {viewshm2}"')
            os.system(f'screen -dSm viewshm bash -c "sleep 5;unbuffer python3 viewshm3.py 1920 1080 100 50 {viewshm2};bash"')
            MOUNTINGOFFLOADING=True
        else:
            #shuffle job started
            #launch camchecker.py
            os.system('screen -dSm camchecker bash -c "python3 camdiagnostics/camchecker.py;echo camchecker;bash"')
            MOUNTINGOFFLOADING=False
    elif plc.JA and MOUNTINGOFFLOADING:            
        if T1posaway==0 and abs(plc.GantryTargetSlot-plc.GantryCurrSlot)<=1:
            T1posaway=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        if T0posaway==0 and abs(plc.GantryTargetSlot-plc.GantryCurrSlot)==0 and abs(plc.GantryTargPosMM-plc.GantryCurrPosMM)<=100:
            T0posaway=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')

    #reset TCDS and CLPS detection once trolleypos within 100mm away from trolleyposdest
    if plc.JOBTYPE=='OFFLOADING' and plc.TrolleyPos==plc.TrolleyPosDest and abs(plc.TrolleyPosTargMM-plc.TrolleyPosCurrMM)<=100:
        for i in range(1,9):
            mcrw.raw_write(f'tcds_corner{i}', 0)
        mcrw.raw_write(f'clps_liftdetected', 0)
        mcrw.raw_write(f'piggyback_liftdetected', 0)
        for i in range(1,5):
            mcrw.raw_write(f'clps_corner{i}', 0)
        for camname in ['ts20b', 'ts20f', 'tl20b', 'tl20f', 'ts4xb', 'ts4xf', 'tl4xb', 'tl4xf']:
            mcrw.raw_write(f'clps_moveoffdetected_{camname}', 0)

    if lastJA and not plc.JA:
        if MOUNTINGOFFLOADING:
            PMNRSLOGFILENAME=f'/opt/captures/PMNRSJOBINFO/{DATE}.txt'
            pmnumbers='|'.join(sorted(mcrw.raw_read('pmnumbers',set())))
            pmnumber_match=mcrw.raw_read('pmnumber_match', 0)
            if pmnumber_match!=0:
                pmnumber_match=datetime.fromtimestamp(pmnumber_match).strftime('%Y-%m-%d_%H-%M-%S')
            printandlog(f'{JOBDATE}_{JOBTIME},{T1posaway},{T0posaway},{pmnumber_match},{DATE}_{TIME},{pmnumbers},{pmnumber}',file=makedirsopen(PMNRSLOGFILENAME,'a'),sep=",")
        MOUNTINGOFFLOADING=False
        #job ended
        mcrw.raw_write('JA',0)
        mcrw.raw_write('Tjobstart',time.time())
        mcrw.raw_write('jobside','x')
        mcrw.raw_write('clps_active',0)
        mcrw.raw_write('tcds_active',0)
        mcrw.raw_write('pmnrstop_active',0)
        mcrw.raw_write('pmnrsside_active',0)
        mcrw.raw_write('hncdstop_active',0)
        mcrw.raw_write('hncdsside_active',0)
        os.system('bash endjob.sh > /dev/null 2>&1') 
        os.system('touch /dev/shm/fs.log') 
        os.system('mv /dev/shm/fs.log /dev/shm/armglog/') 
        try:
            #save logs to lastlogs
            os.system(f'rsync -av /dev/shm/armglog/ /dev/shm/armglog.last/ >/dev/null 2>&1')
            os.makedirs(f'/opt/captures/armglog/{JOBDATE}',exist_ok=True)
            os.system(f'rsync -av /dev/shm/armglog/ /opt/captures/armglog/{JOBDATE}/{JOBTIME} >/dev/null 2>&1')
        except:
            pass
    if 0:
        cv2.imshow('quitter',np.zeros((200,200,3),dtype=np.uint8))
        c=cv2.waitKey(1)    
        if c==ord('q'):
            mcrw.raw_write('JA',0)
            mcrw.raw_write('Tjobstart',time.time())
            os.system('bash killall.sh')
            try:
                os.system(f'rsync -av /dev/shm/armglog/ /dev/shm/armglog.last/ >/dev/null 2>&1')
                os.makedirs(f'/opt/captures/armglog/{JOBDATE}',exist_ok=True)
                os.system(f'rsync -av /dev/shm/armglog/ /opt/captures/armglog/{JOBDATE}/{JOBTIME} >/dev/null 2>&1')
            except:
                pass
            break
    lastJA=plc.JA
    time.sleep(0.1)
