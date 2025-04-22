cd /home/mvizn/Code/mviznARMG
. adocker1
#/dev/shm/gpu0yolo.log
#/dev/shm/gpu1yolo.log
#/dev/null
mkdir -p /opt/captures/rotatelogs
export PYTHONUNBUFFERED=1
bash -c 'while true;do stdbuf -oL ipython docker1/gpu0yolo.ipy;done ' 2>&1 | python3 -u 00_home.src/bin/smarttee.py /opt/captures/rotatelogs/gpu0yolo.log &
bash -c 'while true;do stdbuf -oL ipython docker1/gpu1yolo.ipy;done ' 2>&1 | python3 -u 00_home.src/bin/smarttee.py /opt/captures/rotatelogs/gpu1yolo.log &
bash
#while true;do sleep 1;date;done
