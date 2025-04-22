#version:1
from config.config import *
while True:
    plc = readplc()
    if not(plc.JA) or plc.TLOCK and plc.getEstHoistPos()>6000:break
    canmovecam=plc.CNRSCompleted and not plc.MI
    if canmovecam:
        size=plc.size
        SIDE=plc.SIDE
        for camname in [f'cn{SIDE}sbf', f'cn{SIDE}sbb']:
            print(f'try panning for clps {camname}{size}')
            try:
                cam = eval(camname)
                cam.loadpostxt(f'config/clps/{camname}{size}.txt')
                print(f'success panning for clps {camname}')
            except:
                pass
    time.sleep(5)