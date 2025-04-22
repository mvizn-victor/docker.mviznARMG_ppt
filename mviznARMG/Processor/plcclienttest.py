import psutil
import GPUtil
from config.config import *
import json
import socket
import struct
import binascii
import random
import time
from datetime import date, datetime
import numpy as np
import shutil
import os
from memcachehelper import memcacheRW as mcrw
import pickle

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
    heartbeat=1-heartbeat
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)
    values=[days_field, millis,heartbeat,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def coretemp():
        try:
            temps = psutil.sensors_temperatures()['k10temp']
        except KeyError:
            temps = psutil.sensors_temperatures()['coretemp']
        except AttributeError:
            temps = ''
        finally:
            if temps == '':
                return ''
            else:
                avg_temp = 0.0
                for entry in temps:
                    if entry.label[0:-2] == 'Core':
                        avg_temp += entry.current / 4.0
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
    values[4]=int(coretemp())
    values[5],values[6]=gputemp()  
    values[5]=int(values[5])
    values[6]=int(values[6])
    values[7] = int(psutil.cpu_percent(interval=0.1))
    values[8] = int(psutil.virtual_memory().percent)

    pmnrs_active=time.time()-mcrw.raw_read('pmnrstop_active',0)<1
    pmnrs_processing=time.time()-mcrw.raw_read('pmnrs_processing',0)<1
    pmnumber_match=mcrw.raw_read('pmnumber_match',0)-mcrw.raw_read('Tjobstart',0)>0
    pmnrs_lpread=mcrw.raw_read('pmnrs_lpread',0)
    values[10]=(pmnrs_active*b[0])|\
        (pmnrs_processing*b[1])|\
        (pmnumber_match*b[2])|\
        (pmnrs_lpread*b[3])
    pmnumber_read=mcrw.raw_read('pmnumber_read','')
    values[12:16]=textto4int(pmnumber_read)
    lpnumber_read=mcrw.raw_read('lpnumber_read','')
    values[16:20]=textto4int(lpnumber_read)
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
    hncds_p=time.time()-mcrw.raw_read('last_hncds_p',0)<1
    hncds_a=time.time()-mcrw.raw_read('last_hncds_a',0)<1
    hncds_h=time.time()-mcrw.raw_read('last_hncds_h',0)<1
    values[20]=(hncds_active*b[0])|\
        (hncds_p*b[1])|\
        (hncds_a*b[2])|\
        (hncds_h*b[3])
    print('values20',f'hncds:{values[20]:08b}')
    tcds_active = time.time() - mcrw.raw_read('tcds_active', 0) < 1
    tcds_corners=dict()
    for i in range(1,9):
        tcds_corners[i]=mcrw.raw_read(f'tcds_corner{i}', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    tcds_detected=any(tcds_corners[i] for i in range(1,9))
    values[21]=(tcds_active*b[0])|\
               (tcds_detected*b[1])
    for i in range(4):
        values[21]|=tcds_corners[i+5]*b[i+2]
               
    values[22]=0
    for i in range(4):
        values[22]|=tcds_corners[i+1]*b[i]
    print('values21',f'tcds1:{values[21]:08b}')
    print('values22',f'tcds2:{values[22]:08b}')
    clps_liftdetected = mcrw.raw_read('clps_liftdetected', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0
    clps_active=time.time()-mcrw.raw_read('clps_active',0)<5
    clps_corners=dict()
    for i in range(1,5):
        clps_corners[i]=mcrw.raw_read(f'clps_corner{i}', 0)-mcrw.raw_read(f'Tjobstart', 0)> 0    
    values[24]=(clps_active*b[0])|\
               (clps_liftdetected*b[1])
    for i in range(4):
        values[24]|=clps_corners[i+1]*b[i+2]
    print('values24', f'clps:{values[24]:08b}')
    jobside=mcrw.raw_read('jobside','x')
    if mcrw.raw_read('JA',0)==0:
        jobside='x'
    def landsidecam(camname):
        if 'l' in camname or 'ovtr' in camname:
            return True
        else:
            return False    
    def camstatus(camname):        
        if jobside=='x':return 0
        if jobside=='l' and landsidecam(camname) or jobside=='s' and not landsidecam(camname):
            return time.time()-mcrw.raw_read(f'{camname}lastcamtime',0)>2
        else:
            return 0
    #camera latency
    values[25]=0
    i=0
    for camname in ['ovss','ovls','pmnss','pmnls','cnssbb','cnssbc','cnssbf','cnlsbb']:
        values[25]|=b[i]*camstatus(camname)
        i=i+1
    print('values25',f'cam1:{values[25]:08b}')
    values[26]=0
    i=0
    for camname in ['cnlsbc','cnlsbf','ts20f','ts20b','ts4xf','ts4xb','tl20f','tl20b']:
        values[26]|=b[i]*camstatus(camname)
        i=i+1
    print('values26',f'cam2:{values[26]:08b}')
    values[27]=0
    i=0
    for camname in ['tl4xf','tl4xb','ovtrls','ovtrss']:
        values[27]|=b[i]*camstatus(camname)
        i=i+1
    print('values27',f'cam3:{values[27]:08b}')
    packed_data = packer.pack(*values)

    # print('Sending values =', values)
    # print('Sending values len =', len(values))
    # print('Sending values =', 'sending {!r}'.format(binascii.hexlify(packed_data)))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    while True:
        try:
            s.connect((TCP_IP, TCP_PORT))
            break
        except Exception as e:
            print(e)
            time.sleep(0.5)
            # print(packed_data)            
    s.send(packed_data)
    data = s.recv(BUFFER_SIZE)
    s.close()
    
    DATE=now.strftime("%Y-%m-%d")
    TIME=now.strftime("%H-%M-%S.%f")
    os.makedirs(f"/opt/captures/plclog/",exist_ok=True)
    os.makedirs(f"/opt/captures/plclogout/",exist_ok=True)
    #pickle.dump(data,open(f"/opt/captures/plclog/{DATE}/{DATE}_{TIME}.dat",'wb'))
    #open(f"/opt/captures/plclog/{DATE}/{DATE}_{TIME}.dat",'wb').write(data)    
    #thread = Thread(target=writedata, args=(f"/opt/captures/plclog/{DATE}.dat",data), daemon=True)
    #thread.start()
    T=time.time()
    thread = Thread(target=writedata2, args=(f"/opt/captures/plclog/{DATE}.dat",data,T), daemon=True)    
    thread.start()
    thread = Thread(target=writedata2, args=(f"/opt/captures/plclogout/{DATE}.dat",packed_data,T), daemon=True)
    thread.start()
    if os.path.exists('/tmp/saveplc'):
        #to save plc dat for offline testing
        os.unlink('/tmp/saveplc')
        thread = Thread(target=writedata, args=(f"plc.dat",data), daemon=True)
        thread.start()
    DataR = list(unpacker.unpack(data))    
    #for i in range(2,6):
    #    DataR[i] = ''.join(reversed(f'{ord(DataR[i]):08b}'))
    #print(JA,TLOCK,MI,CNRSCompleted,OFFLOADING,HoistPos)
    T=time.time()
    plc = PLC(DataR, T)
    plc.print()

    mcrw.raw_write('plcdata',(T,DataR))
    Telapse=time.time()-T1
    print(Telapse)
    time.sleep(max(0.5-Telapse,0))


