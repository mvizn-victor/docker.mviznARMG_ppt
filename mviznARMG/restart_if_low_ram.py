#version:hf10
#hf10
#  runall with flag 1 to avoid killing plc screen

import psutil
import os
import sys
from datetime import datetime,timedelta
import time
time.sleep(50)
if psutil.virtual_memory().available/1e9<2:
    print(datetime.now(),file=open('/opt/captures/low_ram_restart.txt','a'))
    #os.system('rm /tmp/launched')
    os.system("bash runall.sh 1")
