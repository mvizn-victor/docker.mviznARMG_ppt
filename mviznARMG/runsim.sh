#version:ehz
#ehz:
#  added DISPLAY which will be present when first ran after calibration
rm /dev/shm/*
sleep 1
cd ~/Code/mviznARMG
touch /dev/shm/simARMG
sleep 1
. a
bash killall.sh
python Processor/workflow.py $1
bash killall.sh
rm /dev/shm/simARMG
