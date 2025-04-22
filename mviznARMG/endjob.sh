#version:1
pkill -f framesharer
pkill -f pmnrstop.py
pkill -f pmnrsside.py
pkill -f pmnrsptz.py
pkill -f hncdstop.py
pkill -f hncdsside.py
pkill -f tcdsptz.py
pkill -f tcds.py
pkill -f clpsptz.py
pkill -f clps.py
pkill -f viewshm
pkill -f clps_maskrcnn_loop.py
pkill -f camchecker.py
pkill -f tcdstx_yolo.py
pkill -f clps_yolo.py
pkill -f clpslift_inception.py
#docker kill tf-docker;docker rm tf-docker
