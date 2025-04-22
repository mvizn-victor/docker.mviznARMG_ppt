import glob
import sys
import time
import os
d=sys.argv[1]
while True:
    for fin,fout in zip(sorted(glob.glob(f'{d}/plcin/*.dat')),sorted(glob.glob(f'{d}/plcout/*.dat'))):
        os.system(f'cp {fin} /tmp/plc.dat')
        os.system(f'cp {fin} /dev/shm/plcin.dat')
        os.system(f'cp {fout} /dev/shm/plcout.dat')                
        time.sleep(0.5)
