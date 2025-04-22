. a
bash killall.sh
bash PMNRS/tfserve.sh &
python PMNRS/textboxdetector.py &
sleep 1
python PMNRS/test_1video.py $1
bash killall.sh
