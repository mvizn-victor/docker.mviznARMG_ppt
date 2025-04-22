screen -S 100_yolo -X quit
screen -S 101_inception -X quit
screen -S 102_pointrend -X quit
cd ~/Code/mviznTLD
. ~/Code/ARMGvenv/bin/activate
export PYTHONPATH=.
screen -dSm 100_yolo bash -c 'while true;do ipython docker1/gpu0yolo.ipy;sleep 1;done'
screen -dSm 101_inception bash -c 'while true;do ipython docker1/gpu0inception.ipy;sleep 1;done'
screen -dSm 102_pointrend bash -c 'while true;do ipython docker2/gpu0pointrend.ipy;sleep 1;done'

