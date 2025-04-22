#version:1
bash endjob.sh 
pkill -f plcclient.py
pkill -f tfserve.sh
pkill -f restarter
pkill -f textboxdetector.py
pkill -f hncdsinception.py
pkill -f hncdstopyolo.py
pkill -f hncdssideyolo.py
pkill -f psfaux
