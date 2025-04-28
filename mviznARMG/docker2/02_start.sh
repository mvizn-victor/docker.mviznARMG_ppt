#cd /home/mvizn/Code/mviznARMG
#. adocker1
#run.sh
export PYTHONPATH=.
echo cd /mviznARMG
cd /mviznARMG
echo "rm /dev/shm/clpsmaskrcnn/*"
rm /dev/shm/clpsmaskrcnn/*

export PYTHONPATH=.
export app="gpu1pointrend"

mkdir -p /opt/captures/screenlogs/$app

screen -dSm "$app" bash -c "
echo running $app
while true; do
    echo running $app
    stdbuf -oL python3 -u docker2/gpu1pointrend.py
    echo $app
    echo rerun
    date
    sleep 1
done 2>&1 | tee -a /opt/captures/screenlogs/$app/log.txt
"

while true;do
    screen -ls
    sleep 1
done