#version: 1.0.1

#%run -i ~/helperfun.ipy
import cv2
import time
import json
import os
from io import StringIO
import traceback


def geterrorstring(e):
    sio=StringIO()
    print("An exception occurred:", e,file=sio)
    print("\nStack trace:",file=sio)
    print(traceback.format_exc(),file=sio)
    return sio.getvalue()
def makedirsf(f):
    os.makedirs(os.path.dirname(f),exist_ok=True)
    return f

def run_in_background(fn):
    import threading    
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper


class C__flaskdisplay:
    """
    onclick(g,x,y)  # x=xdivw,y=ydivh
    """
    def __init__(g,id='001',onclick=None,oncommand=None):
        import random
        g.name=str(random.randint(0,int(1e5)))
        g.bindingdir=makedirsf(f'/dev/shm/flaskdisplay/{id}')
        g.imagef=makedirsf(f'{g.bindingdir}/image.jpg')
        g.lastupdatef=makedirsf(f'{g.bindingdir}/lastupdatef.json')
        g.clickf=makedirsf(f'{g.bindingdir}/clickf.txt')
        g.keypressf=makedirsf(f'{g.bindingdir}/keypressf.txt')
        g.commandf=makedirsf(f'{g.bindingdir}/commandf.txt')
        g.statusf=makedirsf(f'{g.bindingdir}/statusf.txt')
        g.lastclickT=0
        g.lastkeypressT=0
        def def_onclick(g,x,y):
            print('click',x,y)
            pass
        def def_oncommand(g,command):
            print('command',command)
            pass
        if onclick is None:
            g.onclick=def_onclick
        else:
            g.onclick=onclick        
        if oncommand is None:
            g.oncommand=def_oncommand
        else:
            g.oncommand=oncommand        
    def imswk(g,im,wait=0):
        g.update(im)
        g.keyexpire=time.time()+wait/1000
        while 1:
            if time.time()>g.keyexpire and wait>0: return -1
            try:
                keycode=open(g.keypressf).read()
                keycode=int(keycode)
                os.unlink(g.keypressf)
                return keycode
            except KeyboardInterrupt:
                raise
            except:
                pass
            time.sleep(0.001)
    def update(g,im):
        try:
            os.unlink(g.clickf)
        except:
            pass
        if 0:
            try:
                os.unlink(g.keypressf)
            except:
                pass
        if im is None:
            im=np.zeros((720,1280,3))
        try:
            g.lastim
        except:
            g.lastim=None
        if g.lastim is None or g.lastim.shape!=im.shape or (g.lastim!=im).any():
            g.lastim=im
            cv2.imwrite(g.imagef,im)
            g.h,g.w=im.shape[:2]
            print(json.dumps({'T':time.time(),'w':g.w,'h':g.h},indent=2),file=open(g.lastupdatef,'w'))
    def handleclick(g):
        try:
            x,y=open(g.clickf).read().split()
            try:
                g.w
            except:
                g.w=1280
            try:
                g.h
            except:
                g.h=720
            x=int(float(x)*g.w)
            y=int(float(y)*g.h)
            try:
                g.onclick(g,x,y)
                g.onclickerror=''
            except Exception as e:
                g.onclickerror=geterrorstring(e)
            os.unlink(g.clickf)
            return 1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            #print(geterrorstring(e))
            return 0
    def handlecommand(g):
        try:
            command=open(g.commandf).read()
            try:
                g.oncommand(g,command)
                g.oncommanderror=''
            except Exception as e:
                g.oncommanderror=geterrorstring(e)
            os.unlink(g.commandf)
            return 1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return 0
    def listener(g):
        g.kill=1
        #to kill listener if running
        time.sleep(1)
        g.kill=0
        try:
            if g.listeneralive:return
        except:
            print('listeneralive')
        g.listeneralive=1
        while 1:
            if g.kill:break       
            g.handleclick()
            g.handlecommand()
            time.sleep(0.001)
        g.listeneralive=0
    def startlistener(g):
        run_in_background(g.listener)()        
    def click(g,x,y):
        print(x,y,file=open(g.clickf,'w'))
        return 1
    def keypress(g,keycode):
        print(keycode,file=open(g.keypressf,'w'))
        return 1
    def command(g,command):
        print(command,file=open(g.commandf,'w'))
        return 1
    def status(g,s=None):
        if s is None:
            try:
                s=open(g.statusf).read()
                return s
            except:
                return ''
        else:
            print(s,file=open(g.statusf,'w'))
            return str(s)
    def __del__(g):
        g.kill=1
        print('delete')
