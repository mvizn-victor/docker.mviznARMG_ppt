#version:1
import requests
import base64
import cv2
import time
import math
import os
import numpy as np
import sys
import pickle
def gettextboxes(img):
    T=time.time()
    os.makedirs('/dev/shm/pmnrstextdetect/',exist_ok=True)
    cv2.imwrite(f'/dev/shm/pmnrstextdetect/{T}.jpg',img)
    fout=f'/dev/shm/pmnrstextdetect/{T}.pkl'
    while True:
        try:
            res=pickle.load(open(fout,'rb'))
            print(res)
            os.unlink(fout)
            break
        except FileNotFoundError:
            time.sleep(0.001)
        except EOFError:
            time.sleep(0.001)
        except:
            #raise
            time.sleep(0.001)
    return res

def drawtext(x1,y1,x2,y2, outframe, x0, y0,text=None):
    cv2.rectangle(outframe, (x0+x1, y0+y1), (x0+x2, y0+y2), (244, 226, 66), 1)
    cv2.putText(outframe, text, (x0 + x2, y0 + y2), cv2.FONT_HERSHEY_DUPLEX, 1,
                (244, 66, 206))

def OCR(image):
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer).decode('utf8')
    url = "http://localhost:9001/v1/models/AOCR:predict"

    r = requests.post(url=url, json={
        "signature_name": "serving_default",
        "inputs": {
            "input": {"b64": jpg_as_text}
        }
    })
    json = r.json()
    text=json['outputs']['output']
    prob=json['outputs']['probability']
    return text,prob
