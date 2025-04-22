. a
bash killall.sh
python HNCDS/hncdsinception.py &
python HNCDS/test_1video.py $1 &
python CLPS/clpstest6.py
bash killall.sh
