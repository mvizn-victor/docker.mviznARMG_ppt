#version:ehz
#ehz
#  count proc
import os
import sys
proc=' '.join(sys.argv[1:])
psfaux=os.popen('ps faux').read()
N=0
for line in psfaux.split('\n'):
    if 'SCREEN' in line:
        continue
    if 'countproc' in line:
        continue
    if proc in line:
        N+=1
print(N)
