#version:1
import os
import glob
import sys
if 1:
    if len(sys.argv)!=6:
        print('camname oldpan oldtilt newpan newtilt')
        sys.exit(0)
    camname=sys.argv[1]
    oldpan=float(sys.argv[2])
    oldtilt=float(sys.argv[3])
    newpan=float(sys.argv[4])
    newtilt=float(sys.argv[5])
    pandiff=newpan-oldpan
    tiltdiff=newtilt-oldtilt
else:
    pandiff=10
    tiltdiff=5
    camname='cnlsbc'
print('backing up config to config.old')    
os.system('rsync -av config/ config.old')
def readconfig(f):
    out={}
    for line in open(f).read().strip().split():
        k,v=line.split('=')
        if k in ['pan','tilt','zoom']:
            out[k]=(float(v))
    return out
def panconfig(config,v):
    config=config.copy()
    config['pan']=(config['pan']+v+180)%360-180
    return config
def tiltconfig(config,v):
    config=config.copy()
    config['tilt']=(config['tilt']+v)
    return config
def writeconfig(f,config):
    with open(f,'w') as fout:
        for k in ['pan','tilt','zoom']:
            print(f'{k}={config[k]}',file=fout)

#trial run
for oldf in sorted(glob.glob(f'config.old/*/{camname}*')):
    newf=oldf.replace('config.old','config')
    src=readconfig(oldf)
    dest=tiltconfig(panconfig(src,pandiff),tiltdiff)
    print(newf,src,dest)

for oldf in sorted(glob.glob(f'config.old/*/{camname}*')):
    newf=oldf.replace('config.old','config')
    src=readconfig(oldf)
    dest=tiltconfig(panconfig(src,pandiff),tiltdiff)
    writeconfig(newf,dest)
print('camera updated successfully')
