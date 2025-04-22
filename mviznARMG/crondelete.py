from datetime import datetime,timedelta
import shutil
import glob
import sys
import os

def rmtree(d):
    os.system(f'rm -rf {d}')
shutil.rmtree=rmtree

daysvids=24
dayslogs=24
DATE=datetime.today()-timedelta(days=dayslogs)
DATESTR=DATE.strftime('%Y-%m-%d')
for S in ["CLPS","HNCDS","PMNRS","TCDS"]:
    D=f'/opt/captures/{S}/photologs'
    LASTD=f'{D}/{DATESTR}'
    for d in glob.glob(f'{D}/*'):
        if d<LASTD:
            shutil.rmtree(d)
    D=f'/opt/captures/{S}/photologs_raw'
    LASTD=f'{D}/{DATESTR}'
    for d in glob.glob(f'{D}/*'):
        if d<LASTD:
            shutil.rmtree(d)

D=f'/opt/captures/armglog'
LASTD=f'{D}/{DATESTR}'
for d in glob.glob(f'{D}/*'):
    if d<LASTD:
        shutil.rmtree(d)
D=f'/opt/captures/plclog'
LASTD=f'{D}/{DATESTR}.dat'
for d in glob.glob(f'{D}/*.dat'):
    if d<LASTD:
        os.unlink(d)
D=f'/opt/captures/plclogout'
LASTD=f'{D}/{DATESTR}.dat'
for d in glob.glob(f'{D}/*.dat'):
    if d<LASTD:
        os.unlink(d)
D=f'/opt/captures/plclog2'
LASTD=f'{D}/{DATESTR}.dat'
for d in glob.glob(f'{D}/*.dat'):
    if d<LASTD:
        os.unlink(d)
D=f'/opt/captures/plclogout2'
LASTD=f'{D}/{DATESTR}.dat'
for d in glob.glob(f'{D}/*.dat'):
    if d<LASTD:
        os.unlink(d)
D=f'/opt/captures/psfaux'
LASTD=f'{D}/{DATESTR}'
for d in glob.glob(f'{D}/*'):
    if d<LASTD:
        shutil.rmtree(d)

DATE=datetime.today()-timedelta(days=daysvids)
DATESTR=DATE.strftime('%Y-%m-%d')
D='/opt/captures/vids'
LASTD=f'{D}/{DATESTR}'
for d in glob.glob(f'{D}/*'):
    if d<LASTD:
        shutil.rmtree(d)


def get_machine_storage(d):
    result=os.statvfs(d)
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bavail
    giga=1024*1024*1024
    # giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    #print('total_size = %s' % total_size)
    #print('free_size = %s' % free_size)
    return free_size

print('free',get_machine_storage('/opt'))
for D in sorted(glob.glob('/opt/captures/vids/*')):
    if get_machine_storage('/opt')<(1-datetime.now().hour/24)*300:
        shutil.rmtree(D)
    else:
        break        
