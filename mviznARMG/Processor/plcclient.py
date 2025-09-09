#version:id28
#fj18
#  previous
#id28
#  change plcout packet size to 110

import psutil
import GPUtil
from config.config import *
import json
import socket
import struct
import binascii
import random
import numpy as np
import shutil
import os
from memcachehelper import memcacheRW as mcrw
import pickle
from datetime import date
simulation =  os.path.exists('/dev/shm/simARMG')

def writedata(filename,data):
    open(filename,'wb').write(data)
def writedata2(filename,data,T):
    open(filename,'ab').write(int(T*100).to_bytes(5,'big')+data)

PLC_START_DATE = date(1990, 1, 1)

BUFFER_SIZE = 1024
MESSAGE = b"Hello, World!"

packer = struct.Struct('>2i2B'
                       '5h1i'
                       '2B4h4h'
                       '1B'
                       '3B'
                       '1B'
                       '3B'
                       '2B' 
                      )
unpacker = struct.Struct('!1i 1h 4c'
			 '4i'
			 '3h'
			 '2i'
			 '3h'
			 '2i'
			 '2h'
			 '4h'
			 '7h')

def textto4int(s):
    s=s.ljust(8)
    out=[]
    for i in range(0,8,2):
        out.append(ord(s[i])*256+ord(s[i+1]))
    return out
lastJA=False
T0=time.time()
heartbeat=0
salive=False
while True:
    T1=time.time()
    current_milli_time = int(round(time.time() * 1000))
    cpu_temp = random.randint(20, 150)
    gpu0_temp = random.randint(20, 150)
    gpu1_temp = random.randint(20, 150)
    cpu_percent = random.randint(0, 100)
    ram_percent = random.randint(0, 100)
    delta_days = date.today() - PLC_START_DATE
    days_field = int(delta_days.days)
    print("Day:", days_field)
    now = datetime.now()
    since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0))
    print("Time:", int(since_midnight.total_seconds() * 1000))
    millis = int(since_midnight.total_seconds() * 1000)

    if 0:
        values = (days_field, millis, 20, 30, 40, 50, 60, b'R', b'S', b'V', b'D',
              1, 0, 1, 0, 0, 0, 0, 0, b'm', b'V', b'i', b'z', b'n', b'1', b'2', b'3',
              1, 0, 1, 0, 0, 0, 0, 0,
              1, 0, 1, 0, 0, 0, 0, 0,
              1, 0, 1, 0, 0, 0, 0, 0,
              1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0
              )
    #heartbeat=1-heartbeat
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)
    #values=[days_field, millis,heartbeat,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    BYTES=bytearray(152)
    BYTES[0:4]=struct.pack('>i',days_field)
    BYTES[4:8]=struct.pack('>i',millis)        
    BYTES[8:9]=struct.pack('>B',heartbeat)
    def coretemp():
        temps0=psutil.sensors_temperatures()
        if 'k10temp' in temps0:
            temps = temps0['k10temp']
        elif 'coretemp' in temps0:
            temps = temps0['coretemp']
        elif 'zenpower' in temps0:
            temps = temps0['zenpower']
        else:
            print('temp not found set as 99')
            return 99
        avg_temp = 0.0
        for entry in temps:
            if entry.label[0:4] == 'Core':
                avg_temp += entry.current / len(temps)
            # 4-core CPU
            elif entry.label == 'Tdie':
                avg_temp = entry.current
        return avg_temp
    def gputemp():
        if len(GPUtil.getGPUs()) == 2:
            gpu_list = []
            for gpu in GPUtil.getGPUs():
                gpu_list += [gpu.temperature]
            return gpu_list
        elif len(GPUtil.getGPUs()) == 1:
            return [GPUtil.getGPUs()[0].temperature, 0]
        else:
            return [0, 0]
    try:
        coretempthresh=float(open('config/coretempthresh.txt').read().strip())
        BYTES[10:12]=struct.pack('>h',int(coretemp()/coretempthresh*100))
    except:
        BYTES[10:12]=struct.pack('>h',int(coretemp()))
    try:
        gputempthresh=float(open('config/gputempthresh.txt').read().strip())
        gpus=GPUtil.getGPUs()
        if len(gpus)>0:
            BYTES[12:14]=struct.pack('>h',int(gpus[0].temperature/gputempthresh*100))
        if len(gpus)>1:
            BYTES[14:16]=struct.pack('>h',int(gpus[1].temperature/gputempthresh*100))
    except:
        gpus=GPUtil.getGPUs()
        if len(gpus)>0:
            BYTES[12:14]=struct.pack('>h',int(gpus[0].temperature))
        if len(gpus)>1:
            BYTES[14:16]=struct.pack('>h',int(gpus[1].temperature))
    BYTES[16:18]=struct.pack('>h',int(psutil.cpu_percent(interval=0.1)))
    BYTES[18:20]=struct.pack('>h',int(psutil.virtual_memory().percent))
    if len(gpus)>0:
        BYTES[20:22]=struct.pack('>h',int(gpus[0].load*100))
    if len(gpus)>1:
        BYTES[22:24]=struct.pack('>h',int(gpus[1].load*100))
    pmnrs_active=time.time()-mcrw.raw_read('pmnrstop_active',0)<3
    pmnrs_processing=time.time()-mcrw.raw_read('pmnrs_processing',0)<3
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)-mcrw.raw_read('Tjobstart',0)>0
    pmnrs_lpread=mcrw.raw_read('pmnrs_lpread',0)
    BYTES[24]|=(pmnrs_active*b[0])|\
        (pmnrs_processing*b[1])|\
        (pmnumber_match*b[2])|\
        (pmnrs_lpread*b[3])
    print('BYTES24',f'pmnrs:{BYTES[24]:08b}')
    #if pmnrs_active:
    if 1:
        pmnumber_read=mcrw.raw_read('pmnumber_read','') 
        lpnumber_read=mcrw.raw_read('lpnumber_read','')
    else:
        pmnumber_read=''
        lpnumber_read=''
    print('pmnumber_read:',pmnumber_read)
    print('lpnumber_read:',lpnumber_read)
    BYTES[26:34]=pmnumber_read.ljust(8).encode('utf8')
    BYTES[34:42]=lpnumber_read.ljust(8).encode('utf8')
    #pmnrs
    #10.0 active
    #10.1 processing
    #10.2 pm match
    #10.3 lp read
    #12 pmnumber
    #16 lpnumber

    #+10
    #human hand head
    hncdstop_active=time.time()-mcrw.raw_read('hncdstop_active',0)<1
    hncdsside_active=time.time()-mcrw.raw_read('hncdsside_active',0)<1
    hncds_active=hncdstop_active and hncdsside_active 
    hncds_processing=time.time()-mcrw.raw_read('hncds_processing',0)<1
    hncds_p=time.time()-mcrw.raw_read('last_hncds_p',0)<5
    hncds_a=time.time()-mcrw.raw_read('last_hncds_a',0)<5
    hncds_h=time.time()-mcrw.raw_read('last_hncds_h',0)<5
    BYTES[42]=(hncds_active*b[0])|\
        (hncds_p*b[1])|\
        (hncds_a*b[2])|\
        (hncds_h*b[3])|\
        (hncds_processing*b[4])
    print('BYTES42',f'hncds:{BYTES[42]:08b}')
    tcds_active = time.time() - mcrw.raw_read('tcds_active', 0) < 1
    tcds_processing = time.time() - mcrw.raw_read('tcds_processing', 0) < 3

    tcds_corners=dict()
    for i in range(1,9):
        tcds_corners[i]=mcrw.raw_read(f'tcds_corner{i}', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    tcds_detected=any(tcds_corners[i] for i in range(1,9))
    BYTES[43]=(tcds_active*b[0])|\
               (tcds_detected*b[1])|\
               (tcds_processing*b[6])
    for i in range(4):
        BYTES[43]|=tcds_corners[i+5]*b[i+2]
               
    BYTES[44]=0
    for i in range(4):
        BYTES[44]|=tcds_corners[i+1]*b[i]
    piggyback_liftdetected = mcrw.raw_read('piggyback_liftdetected', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    if piggyback_liftdetected:
        for i in range(4):
            BYTES[44]|=b[i+4]
    #TCDS BYTES45 active if corner casting detected
    BYTES[45]=0
    for i,camtype in enumerate(['cf','cb','cc','tf','tb']):
        BYTES[45]|=(mcrw.raw_read(f'tcds_{camtype}',0)-mcrw.raw_read(f'Tjobstart',0)>0)*b[i]

    #id28
    for i,camtype in enumerate(['cf','cb','cc','tf','tb']):
        BYTEADDR=100+i*2
        BYTES[BYTEADDR:BYTEADDR+2]=struct.pack('>h',mcrw.raw_read(f'tcds_n{camtype}',0))


    print('BYTES43',f'tcds1:{BYTES[43]:08b}')
    print('BYTES44',f'tcds2:{BYTES[44]:08b}')
    print('BYTES45',f'tcds3:{BYTES[45]:08b}')
    clps_liftdetected = mcrw.raw_read('clps_liftdetected', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    clps_active=time.time()-mcrw.raw_read('clps_active',0)<5
    clps_processing=time.time()-mcrw.raw_read('clps_processing',0)<5
    clps_corners=dict()
    for i in range(1,5):
        clps_corners[i]=mcrw.raw_read(f'clps_corner{i}', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    clps_moveoffdetected=0
    for camname in ['ts20b', 'ts20f', 'tl20b', 'tl20f', 'ts4xb', 'ts4xf', 'tl4xb', 'tl4xf']:
        clps_moveoffdetected+=mcrw.raw_read(f'clps_moveoffdetected_{camname}', 0)-mcrw.raw_read(f'Tjobstart', 0)>0
    if clps_moveoffdetected>=2:
        clps_moveoffdetected=1
        clps_liftdetected=0
    else:
        clps_moveoffdetected=0

    BYTES[46]=(clps_active*b[0])|\
               (clps_liftdetected*b[1])|\
               (clps_moveoffdetected*b[6])|\
               (clps_processing*b[7])
    for i in range(4):
        BYTES[46]|=clps_corners[i+1]*b[i+2]
    print('BYTES46', f'clps:{BYTES[46]:08b}')
    jobside=mcrw.raw_read('jobside','x')
    if mcrw.raw_read('JA',0)==0:
        jobside='x'
    def landsidecam(camname):
        if 'l' in camname or 'ovtr' in camname:
            return True
        else:
            return False
    def seasidecam(camname):
        if 'l' not in camname or 'ovtr' in camname:
            return True
        else:
            return False                    
    def camstatus(camname):        
        if time.time()-mcrw.raw_read('Tjobstart',0)<2:return 0
        if jobside=='x':return 0
        if jobside=='l' and landsidecam(camname) or jobside=='s' and seasidecam(camname):
            return time.time()-mcrw.raw_read(f'{camname}lastcamtime',0)>2
        else:
            return 0
    def camlatency(camname):
        if time.time()-mcrw.raw_read('Tjobstart',0)<2:return 0
        if jobside=='x':return 0
        if jobside=='l' and landsidecam(camname) or jobside=='s' and seasidecam(camname):
            return max(-32767,min(int((time.time()-mcrw.raw_read(f'{camname}lastcamtime',0))*1000),32767))
        else:
            return 0
            
    #camera latency
    BYTES[47]=0
    i=0
    for camname in ['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']:
        BYTES[47]|=b[i]*camstatus(camname)
        i=i+1
    print('BYTES47',f'cam1:{BYTES[47]:08b}')
    BYTES[48]=0
    i=0
    for camname in ['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']:
        BYTES[48]|=b[i]*camstatus(camname)
        i=i+1
    print('BYTES48',f'cam2:{BYTES[48]:08b}')
    BYTES[49]=0
    i=0
    for camname in ['tl4xf','tl4xb','ovtrls','ovtrss']:
        BYTES[49]|=b[i]*camstatus(camname)
        i=i+1
    print('BYTES49',f'cam3:{BYTES[49]:08b}')
    
    allcams=['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']+['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']+['tl4xf','tl4xb','ovtrls','ovtrss']
    emptycamdict={}
    for cam in allcams:
        emptycamdict[cam]=0
    blur=mcrw.raw_read('blur',emptycamdict)
    BYTES[50]=0
    i=0
    for camname in ['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']:
        BYTES[50]|=b[i]*blur[camname]
        i=i+1
    print('BYTES50',f'blurcam1:{BYTES[50]:08b}')
    BYTES[51]=0
    i=0
    for camname in ['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']:
        BYTES[51]|=b[i]*blur[camname]
        i=i+1
    print('BYTES51',f'blurcam2:{BYTES[51]:08b}')
    BYTES[52]=0
    i=0
    for camname in ['tl4xf','tl4xb','ovtrls','ovtrss']:
        BYTES[52]|=b[i]*blur[camname]
        i=i+1
    print('BYTES52',f'blurcam3:{BYTES[52]:08b}')
    
    waterdrop=mcrw.raw_read('waterdrop',emptycamdict)
    BYTES[53]=0
    i=0
    for camname in ['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']:
        BYTES[53]|=b[i]*waterdrop[camname]
        i=i+1
    print('BYTES53',f'wdcam1:{BYTES[53]:08b}')
    BYTES[54]=0
    i=0
    for camname in ['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']:
        BYTES[54]|=b[i]*waterdrop[camname]
        i=i+1
    print('BYTES54',f'wdcam2:{BYTES[54]:08b}')
    BYTES[55]=0
    i=0
    for camname in ['tl4xf','tl4xb','ovtrls','ovtrss']:
        BYTES[55]|=b[i]*waterdrop[camname]
        i=i+1
    print('BYTES55',f'wdcam3:{BYTES[55]:08b}')
    print('BYTES8485',BYTES[84:86])
    i=0
    for camname in ['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']+['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']+['tl4xf','tl4xb','ovtrls','ovtrss']:
        BYTES[60+2*i:60+2*i+2]=struct.pack('>h',camlatency(camname))
        i=i+1
                
    #packed_data = packer.pack(*values)
    packed_data=BYTES
    # print('Sending values =', values)
    # print('Sending values len =', len(values))
    # print('Sending values =', 'sending {!r}'.format(binascii.hexlify(packed_data)))
    if not simulation:
        while 1:
            try:
                if not salive:
                    try:
                        s.close()
                    except KeyboardInterrupt:
                        raise
                    except:
                        pass
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.0)
                    s.connect((TCP_IP, TCP_PORT))
                    salive=True
                if os.path.exists('/tmp/sim_corrupt_plc'):
                    os.unlink('/tmp/sim_corrupt_plc')
                    s.send(packed_data[:4])
                s.send(packed_data)
                print('sent length:',len(packed_data))
                data = s.recv(BUFFER_SIZE)            
                assert len(data)==102,'data length not 102'
                break
            except KeyboardInterrupt:
                raise
            except AssertionError as e:
                print(e.args[0])
            except Exception as e:
                salive=False
                print(e)
                try:
                    s.close()
                except KeyboardInterrupt:
                    raise
                except:
                    pass
                print('plc connection fail... wait 1s to reconnect...')
                for t in range(1,0,-1):
                    print(t)
                    time.sleep(1)
        T=time.time()
    else:
        T,data=mcrw.raw_read('simARMGplcdata',[time.time(),bytearray(102)])
    DATE=now.strftime("%Y-%m-%d")
    TIME=now.strftime("%H-%M-%S.%f")
    os.makedirs(f"/opt/captures/plclog2/",exist_ok=True)
    os.makedirs(f"/opt/captures/plclogout2/",exist_ok=True)
    #pickle.dump(data,open(f"/opt/captures/plclog/{DATE}/{DATE}_{TIME}.dat",'wb'))
    #open(f"/opt/captures/plclog/{DATE}/{DATE}_{TIME}.dat",'wb').write(data)    
    #thread = Thread(target=writedata, args=(f"/opt/captures/plclog/{DATE}.dat",data), daemon=True)
    #thread.start()
    thread = Thread(target=writedata2, args=(f"/opt/captures/plclog2/{DATE}.dat",data,T), daemon=True)    
    thread.start()
    thread = Thread(target=writedata2, args=(f"/opt/captures/plclogout2/{DATE}.dat",packed_data,T), daemon=True)
    thread.start()
    
    thread = Thread(target=writedata, args=(f"/dev/shm/plcin.dat",data), daemon=True)
    thread.start()
    thread = Thread(target=writedata, args=(f"/dev/shm/plcout.dat",packed_data), daemon=True)
    thread.start()    
    if os.path.exists('/tmp/saveplc'):
        #to save plc dat for offline testing
        os.unlink('/tmp/saveplc')
        thread = Thread(target=writedata, args=(f"plc.dat",data), daemon=True)
        thread.start()
    #DataR = list(unpacker.unpack(data))    
    #for i in range(2,6):
    #    DataR[i] = ''.join(reversed(f'{ord(DataR[i]):08b}'))
    #print(JA,TLOCK,MI,CNRSCompleted,OFFLOADING,HoistPos)
    plc = PLC2(data, T)
    plc.print()
    #VA echo heartbeat back to plc
    heartbeat=plc.heartbeat_echo
    mcrw.raw_write('plcdata',(T,data))
    Telapse=time.time()-T1
    if Telapse>0.5:Telapse=0.5
    print(Telapse)
    time.sleep(max(0.5-Telapse,0))


