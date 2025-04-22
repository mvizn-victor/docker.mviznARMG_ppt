#version: 1.0.0

from io import StringIO
import traceback
def geterrorstring(e):
    sio=StringIO()
    print("An exception occurred:", e,file=sio)
    print("\nStack trace:",file=sio)
    print(traceback.format_exc(),file=sio)
    return sio.getvalue()
