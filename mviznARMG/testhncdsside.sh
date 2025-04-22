. a
bash killall.sh
gnome-terminal --title=hncdsinception -- bash -c "unbuffer python HNCDS/hncdsinception.py;echo hncdsinception;bash"
gnome-terminal --title=hncdstopyolo -- bash -c "unbuffer python HNCDS/hncdstopyolo.py;echo hncdstopyolo;bash"
gnome-terminal --title=hncdssideyolo -- bash -c "unbuffer python HNCDS/hncdssideyolo.py;echo hncdssideyolo;bash"
python HNCDS/hncdsside.py $1
bash killall.sh
