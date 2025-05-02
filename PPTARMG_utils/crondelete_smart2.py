#version:ie02
#ie02:
# specify target_percent_free:e.g. 10p = target 10% free disk space
# without p at the end is mb to keep: 10000 = keep 10GB deletables folders starting with %Y-%m-%d until year 2099
# dry run
import os
import time
from datetime import datetime
import re
import shutil
import sys
def get_usable_disk_size(path="/opt"):
    stat = os.statvfs(path)
    block_size = stat.f_frsize

    total_blocks = stat.f_blocks
    available_blocks = stat.f_bavail
    used_blocks = total_blocks - stat.f_bfree

    # Calculate in bytes
    used = used_blocks * block_size
    available = available_blocks * block_size
    usable_total = used + available  # excludes reserved blocks

    def to_gb(bytes_val):
        return bytes_val / (1024 ** 3)
    return used+available
def get_disk_free_space(path="/opt"):
    stat = os.statvfs(path)
    free_space_bytes = stat.f_frsize * stat.f_bavail  # f_bavail: free blocks available to non-superuser
    return free_space_bytes

if os.path.exists('/tmp/deleting'):
    print('already running. exiting')
    exit()

dryrun=0
try:
    if sys.argv[2]=='1':
        dryrun=1
        print('dry run')
except:
    pass
    
try:
    if sys.argv[1][-1:]=='p':
        target_percent_free=eval(sys.argv[1][:-1])
        disksize=get_usable_disk_size()/1e6
        free=get_disk_free_space()/1e6
        target_free=target_percent_free/100*disksize
        mbtodelete=max(0,(target_free-free))
        print('target_percent_free: above',target_percent_free//1)
        print('disksize(mb):',disksize//1)
        print('current free(mb):',free//1)
        print('target free(mb): above',target_free//1)
        print('todelete(mb):',mbtodelete//1)
        if mbtodelete<=0:
            print('todelete(mb)<=0, no need to delete')
            exit()
    else:
        mbtokeep=eval(sys.argv[1])
        print('mbtokeep:',mbtokeep)
except:
    print('args: mbtokeep(eg 4e6=4TB) [dryrun]')
    print('or target_percent_free if ends with "p" (eg 10p=free until 10% of disk size free)')
    raise
os.system('touch /tmp/deleting')

try:

    print("ran",datetime.now())
    T0=time.time()
    open('/tmp/optfoldersize.txt','w').write(os.popen("find /opt/captures -type d -name '20*' -print0|xargs -0 du -s").read())
    s=open('/tmp/optfoldersize.txt').read()
    Telapse=time.time()-T0
    print('took',Telapse,'seconds')

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

    #i.e. target_total_mb
    try:
        mbtokeep=max(total_mb-mbtodelete,0)
        print('total_mb of deletables',total_mb)
        print('mbtodelete',mbtodelete)
        print('mbtokeep',mbtokeep)
    except:
        pass

    l__D_fmb_f.sort()
    lastD=None
    for D,f_mb,f in l__D_fmb_f:
        if total_mb<=mbtokeep:
            print(f'total_mb<={mbtokeep//1}','exiting')
            break    
        try:
            lastD=D
            print('deleting',f)
            if not dryrun:
                shutil.rmtree(f)
            total_mb-=f_mb
            print('freed',f_mb//1,'total_mb',total_mb//1)
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
                    print('freed',f_mb//1,'total_mb',total_mb//1)
                except:
                    print('fail delete',f)
    print()
finally:
    os.system('rm /tmp/deleting')
