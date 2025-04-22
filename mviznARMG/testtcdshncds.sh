. a
bash killall.sh
python HNCDS/hncdsinception.py &
python HNCDS/test_1video.py $1 &
python TCDS/detect_custom_subyolo.py $1
bash killall.sh
