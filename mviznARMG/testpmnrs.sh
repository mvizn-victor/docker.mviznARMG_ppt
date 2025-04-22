. a
bash killall.sh
gnome-terminal --title=tfserve -- bash -c "unbuffer bash PMNRS/tfserve.sh;echo tfserve;bash"
gnome-terminal --title=textboxdetector -- bash -c "unbuffer python PMNRS/textboxdetector.py;echo textboxdetector;bash"
gnome-terminal --title=hncdstopyolo -- bash -c "unbuffer python HNCDS/hncdstopyolo.py;echo hncdstopyolo;bash"
python PMNRS/test_1image.py $1
bash killall.sh
