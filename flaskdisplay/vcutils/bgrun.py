#version: 1.0.0

from collections import deque
from io import StringIO
import threading
def run_in_background(func):
    def wrapper(*args, **kwargs):
        # Create a new thread and run the function in it
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return wrapper
def run_in_background2(func,g=None):
    if g is None:
        g=G()
    def wrapper(*args, **kwargs):
        kwargs['g']=g
        # Create a new thread and run the function in it
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return g
    return wrapper
class C__stringqueue:
    def __init__(self,N=10):
        self.N=N
        self.q=[]
        pass
    def print(self,*kargs,**kwargs):
        self.q.append(prints(*kargs,**kwargs))
        self.q=self.q[-self.N:]    
    def s(self):
        print(''.join(self.q))

def prints(*kargs,**kwargs):
    sio=StringIO()
    print(*kargs,**kwargs,file=sio)
    return sio.getvalue()
def demorun(g):
    """
    try:
        dg
    except:
        dg={}
    runname='demorun'
    runfun=eval(runname)
    try:
        g=dg[runname]
    except:
        dg[runname]=G()
        g=dg[runname]
    run_in_background(runfun)(g)
    """
    global killallbgrun
    killallbgrun=0
    g.kill=0
    g.done=0
    g.s=C__stringqueue(5)
    for g.i in range(1000):
        if killallbgrun or g.kill:raise
        g.s.print(datetime.now(),g.i)
        time.sleep(1)
    g.done=1
