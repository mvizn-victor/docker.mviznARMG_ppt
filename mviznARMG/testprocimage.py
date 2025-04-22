from Utils.helper import *
im=cv2.imread('sample.jpg')
procname='hncdssideyolo'
procname='hncdstopyolo'
procname='hncdsinception'
l__procname="""
hncdstopyolo
hncdssideyolo
hncdsinception
tcdsyolo
tcdssubyolo
tcdstx
clps_yolo
clpsmaskrcnn
""".strip().split('\n')
for procname in l__procname:
    print(procname)
    print(procimage(procname,im))
