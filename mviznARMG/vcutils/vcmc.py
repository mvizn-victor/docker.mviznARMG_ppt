#version: 1.1.0
#1.1.0
#  use fcntl for lock

import time
import pickle
import os
import fcntl
import sys
mcdir='/dev/shm/VCMC'

class VCMC:
    def __init__(self, mcdir='/dev/shm/VCMC'):
        self.mcdir = mcdir
        os.makedirs(self.mcdir, exist_ok=True)

    def _lock_file(self, filepath):
        file = open(filepath, 'w+')
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        return file

    def _unlock_file(self, file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        file.close()

    def get(self, key):
        valfile = f'{self.mcdir}/{key}.val'
        if not os.path.exists(valfile):
            return None

        try:
            with open(valfile, 'rb') as f:
                # Attempt to acquire a shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                ret = pickle.load(f)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return ret
        except (FileNotFoundError, EOFError):
            return None
        except BlockingIOError:
            # Handle the case where the file is exclusively locked
            for i in range(1000):
                time.sleep(0.0001)
                try:
                    with open(valfile, 'rb') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                        ret = pickle.load(f)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        return ret
                except (FileNotFoundError, EOFError, BlockingIOError):
                    continue
            return None

    def set(self, key, v):
        valfile = f'{self.mcdir}/{key}.val'
        lockfile = f'{self.mcdir}/{key}.lock' # Explicit lock file for writing

        try:
            # Use an explicit lock file to manage exclusive access for writing
            with open(lockfile, 'w') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                with open(valfile, 'wb') as val:
                    pickle.dump(v, val)
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            return True
        except IOError:
            return False

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
    valfile = f'{mc.mcdir}/{key}.val'
    lockfile = f'{mc.mcdir}/{key}.lock'
    out = None
    try:
        with open(lockfile, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            if os.path.exists(valfile):
                with open(valfile, 'rb+') as val_f:
                    try:
                        v = pickle.load(val_f)
                        if len(v) > 0:
                            out = v.pop(0)
                            val_f.seek(0)
                            pickle.dump(v, val_f)
                            val_f.truncate()
                    except EOFError:
                        pass # File might be empty
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    except IOError:
        pass
    return out

def raw_append(key,value):
    valfile = f'{mc.mcdir}/{key}.val'
    lockfile = f'{mc.mcdir}/{key}.lock'
    try:
        with open(lockfile, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            v = raw_read(key, [])
            v.append(value)
            with open(valfile, 'wb') as val_f:
                pickle.dump(v, val_f)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return True
    except IOError:
        return False