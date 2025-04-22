crane='7209'
wsuri='ws://10.140.98.1:17020'
block='TQ02'

from Utils.helper import *
from config.cornerx import cornerx
TCP_IP = '10.148.156.98'
#TCP_IP='localhost'
TCP_PORT = 2009

#ovtrls=AxisCamera('10.140.48.131','root','pass')
ovtrls=AxisCamera('10.140.98.3','root','pass')
ovtrss=AxisCamera('10.140.98.4','root','pass')
ovls=AxisCamera('10.140.98.5','root','pass')
ovss=AxisCamera('10.140.98.6','root','pass')
cnlsbf=AxisCamera('10.140.98.11','root','pass')
cnlsbb=AxisCamera('10.140.98.12','root','pass')
cnlsbc=AxisCamera('10.140.98.13','root','pass')
tl4xb=AxisCamera('10.140.98.14','root','pass')
tl20b=AxisCamera('10.140.98.15','root','pass')
tl20f=AxisCamera('10.140.98.16','root','pass')
tl4xf=AxisCamera('10.140.98.17','root','pass')
pmnls=AxisCamera('10.140.98.18','root','pass')
cnssbf=AxisCamera('10.140.98.19','root','pass')
cnssbb=AxisCamera('10.140.98.20','root','pass')
cnssbc=AxisCamera('10.140.98.21','root','pass')
ts4xf=AxisCamera('10.140.98.22','root','pass')
ts20f=AxisCamera('10.140.98.23','root','pass')
ts20b=AxisCamera('10.140.98.24','root','pass')
ts4xb=AxisCamera('10.140.98.25','root','pass')
pmnss=AxisCamera('10.140.98.26','root','pass')
axis=AxisCamera('192.168.10.132','root','pass')
camidip="""
ovtrls 10.140.98.3
ovtrss 10.140.98.4
ovls 10.140.98.5
ovss 10.140.98.6
cnlsbf 10.140.98.11
cnlsbb 10.140.98.12
cnlsbc 10.140.98.13
tl4xb 10.140.98.14
tl20b 10.140.98.15
tl20f 10.140.98.16
tl4xf 10.140.98.17
pmnls 10.140.98.18
cnssbf 10.140.98.19
cnssbb 10.140.98.20
cnssbc 10.140.98.21
ts4xf 10.140.98.22
ts20f 10.140.98.23
ts20b 10.140.98.24
ts4xb 10.140.98.25
pmnss 10.140.98.26
""".strip()

#codec='h264'
codec='mjpg'
if 0:
    pass
elif 1:
    videoinput=[]
    for line in camidip.split('\n'):
        camid,camip=line.split()
        if camid.startswith('#'):continue
        if camid.startswith('cn'):
            if codec=='h264':
                videoinput.append([camid,f'rtsp://root:P456YC_pptcam@{camip}/axis-media/media.amp?videocodec=h264&videomaxbitrate=1024&fps=25&resolution=1280x720'])
            else:
                videoinput.append([camid,f'!root:P456YC_pptcam@{camip}:10'])
        else:
            if codec=='h264':            
                videoinput.append([camid,f'rtsp://root:P456YC_pptcam@{camip}/axis-media/media.amp?videocodec=h264&videomaxbitrate=1024&fps=25'])
            else:
                videoinput.append([camid,f'!root:P456YC_pptcam@{camip}:5'])
        if 0: #DIVA
            if camid.startswith('ovtr'):
                videoinput[-1].append((720,1280))
            else:
                videoinput[-1].append((1280,720))
else:
    videoinput=[]
    for line in camidip.split('\n'):
        camid,camip=line.split()
        if camid.startswith('#'):continue
        videoinput.append([camid,f'/mnt/NFSDIR/RawVideos/ARMG/7110/2019-08-23/{camid}-11_00.mp4'])

