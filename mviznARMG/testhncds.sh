. a
bash killall.sh
gnome-terminal --title=hncdsinception -- bash -c "unbuffer python HNCDS/hncdsinception.py;echo hncdsinception;bash"
gnome-terminal --title=hncdstopyolo -- bash -c "unbuffer python HNCDS/hncdstopyolo.py;echo hncdstopyolo;bash"
gnome-terminal --title=hncdssideyolo -- bash -c "unbuffer python HNCDS/hncdssideyolo.py;echo hncdssideyolo;bash"
rm /dev/shm/test_1video*.txt
unbuffer python HNCDS/test_1video.py $1 > /dev/shm/test_1video.txt 2>&1 &
unbuffer python HNCDS/test_1videoside.py $1 > /dev/shm/test_1videoside.txt 2>&1 &
watch -n0.5 'tail /dev/shm/test_1video*.txt'
bash killall.sh
