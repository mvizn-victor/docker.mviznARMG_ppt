import time
import os
app='workflow'
script='Processor/workflow.py'
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
os.system(template.safe_substitute(app=app,script=script))
while 1:
    os.system('screen -ls')
    time.sleep(1)