#version: 1.0.0

import time
import pickle
import os
import sys
mcdir='/dev/shm/VCMC'
class VCMC:
    def get(self,key):
        os.makedirs(mcdir,exist_ok=True)
        lockfile=f'{mcdir}/{key}.lock'
        valfile=f'{mcdir}/{key}.val'
        if 0:
            while os.path.exists(lockfile):
                time.sleep(0.0001)
            try:
                open(lockfile,'w')
                ret=pickle.load(open(valfile,'rb'))            
            except:
                ret=None
            finally:
                try:
                    os.unlink(lockfile)
                except:
                    pass
        ret=None
        if os.path.exists(valfile):
            for i in range(1000):
                try:
                    ret=pickle.load(open(valfile,'rb'))            
                    break
                except:
                    time.sleep(0.0001)
        return ret
    def set(self,key,v):
        os.makedirs(mcdir,exist_ok=True)
        lockfile=f'{mcdir}/{key}.lock'
        valfile=f'{mcdir}/{key}.val'
        while os.path.exists(lockfile):
            time.sleep(0.0001)
        try:
            open(lockfile,'w')
            ret=pickle.dump(v,open(valfile,'wb'))
        except:
            ret=None
        finally:
            try:
                os.unlink(lockfile)
            except:
                pass
        return ret
mc=VCMC()    

def raw_read(key,default=None):
    v = mc.get(key)
    if v is None:
        return default
    else:
        return v
        
def raw_write(key,value):
    return mc.set(key,value)

def raw_popleft(key):
    v = raw_read(key,[])
    if len(v)>0:
        out=v[0]
        v=v[1:]
        mc.set(key,v)
        return out
    else:
        return None

def raw_append(key,value):
    v = raw_read(key,[])
    v.append(value)
    return mc.set(key,v)
