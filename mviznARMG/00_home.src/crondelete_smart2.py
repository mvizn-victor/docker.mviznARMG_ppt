import os
import time
from datetime import datetime
import re
import shutil
if os.path.exists('/tmp/deleting'):
    print('already running. exiting')
    exit()
os.system('touch /tmp/deleting')
dryrun=0
mbtokeep=4e6
try:
    print("ran",datetime.now())
    T0=time.time()
    open('/tmp/optfoldersize.txt','w').write(os.popen("find /opt/captures -type d -name '20*' -print0|xargs -0 du -s").read())
    s=open('/tmp/optfoldersize.txt').read()
    Telapse=time.time()-T0
    print('took',Telapse)

    total_mb=0
    l__D_fmb_f=[]
    for line in s.strip().split('\n'):
        size,f=line.split('\t')
        f_mb=int(size)/1000
        try:
            D=re.findall('20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]',f)[0]
            l__D_fmb_f.append((D,f_mb,f))
            total_mb+=f_mb
        except:
            pass    

    l__D_fmb_f.sort()
    lastD=None
    for D,f_mb,f in l__D_fmb_f:
        if total_mb<=mbtokeep:
            print(f'total_mb<={mbtokeep}','exiting')
            break    
        try:
            lastD=D
            print('deleting',f)
            if not dryrun:
                shutil.rmtree(f)
            total_mb-=f_mb
            print('freed',f_mb,'total_mb',total_mb)
        except:
            print('fail delete',f)


    if lastD is not None:    
        for D,f_mb,f in l__D_fmb_f:
            if D>lastD:
                break    
            if D==lastD:
                try:
                    print('deleting',f)
                    if not dryrun:
                        shutil.rmtree(f)
                    total_mb-=f_mb        
                    print('freed',f_mb,'total_mb',total_mb)
                except:
                    print('fail delete',f)
    print()
finally:
    os.system('rm /tmp/deleting')
