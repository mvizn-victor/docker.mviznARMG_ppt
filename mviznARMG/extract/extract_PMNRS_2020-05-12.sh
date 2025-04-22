. a
bash killall.sh
bash PMNRS/tfserve.sh &
python PMNRS/textboxdetector.py &
sleep 1
python extract/extract_PMNRS_2020-05-12.py
bash killall.sh
