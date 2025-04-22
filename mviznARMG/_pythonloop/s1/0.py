#0.py
import numpy as np
print(np.__version__,'numpy')
 
from vcutils.helperfun import *
from vcutils.geterrorstring import *
from vcutils.RunIfChanged import *
import inspect

import sys
import threading
import os


class Tee:
    def __init__(self, file_path):
        self.console_out = sys.__stdout__
        self.console_err = sys.__stderr__
        self.file_path = file_path
        self.lock = threading.Lock()
        self._open_file()
        self.stdout = self._TeeStream(self.console_out, self)
        self.stderr = self._TeeStream(self.console_err, self)

    def _open_file(self):
        self.file = open(self.file_path, 'a+', buffering=1)  # line-buffered

    class _TeeStream:
        def __init__(self, console_stream, parent):
            self.console_stream = console_stream
            self.parent = parent

        def write(self, data):
            with self.parent.lock:
                self.console_stream.write(data)
                self.console_stream.flush()
                self.parent.file.write(data)
                self.parent.file.flush()

        def flush(self):
            with self.parent.lock:
                self.console_stream.flush()
                self.parent.file.flush()

    def start(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def stop(self):
        sys.stdout = self.console_out
        sys.stderr = self.console_err

    def clear(self):
        with self.lock:
            self.file.close()
            self.file = open(self.file_path, 'w', buffering=1)  # truncate safely
            self.file.flush()
            #print("[Log file cleared]", file=self.console_out)

    def close(self):
        with self.lock:
            self.file.close()

tee = Tee("/dev/shm/s1.log")
tee.start()

runIfChanged=RunIfChanged('_pythonloop/s1/1.py')
runIfChanged.add('_pythonloop/s1/2.py')
while 1:
    try:
        if runIfChanged.checkchange():
            tee.clear()
            time.sleep(0.1)
            try:
                runIfChanged.runifchanged(globals())
            except Exception as e:
                print(geterrorstring(e))
            pass
        time.sleep(1)
    except KeyboardInterrupt:
        __response__=input("KeyboardInterrupt Quit(y=yes):")
        if __response__.lower()=='y':
            break
    time.sleep(0.1)

    
