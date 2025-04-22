#version: 1.0.0

import pickle
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, Response
from datetime import datetime,timedelta
import re
import glob
import threading
import time
import os
import shutil
import json
import os
from pyquery import PyQuery as pq
import os
from vcutils.C__flaskdisplay import C__flaskdisplay
from vcutils.geterrorstring import geterrorstring
import cv2
import numpy as numpy
import sys
app = Flask(__name__)

def myhash(s):
    import hashlib
    return hashlib.md5(s.encode('utf8')).hexdigest()

def isalphanumeric(k):
    import re
    return re.match('^[a-zA-Z0-9._]+$',k)

def fix(k):
    k=k.lower()
    k=re.sub('[!@#$%^&*()_+\\[\\]{}\\|;\',./:"<>?]',' ',k)
    k=' '.join(k.strip().split())
    return k
def makedirsf(f):
    os.makedirs(os.path.dirname(f),exist_ok=1)
    return f
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shutdown', methods=['GET'])
def shutdown():
    # Optionally, you can include some authentication here to ensure
    # that not just anyone can shut down your app.
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    # For a standard Flask development server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')        
    func()

@app.route('/<id>/click/<float:x>/<float:y>', methods=['GET'])
def displayclick(id,x,y):    
    #return f'{id} {x} {y}'
    try:
        C__flaskdisplay(id=id).click(x,y)        
        return json.dumps({'status':'ok','response':f'click {x} {y}'},indent=2)
    except Exception as e:
        error=geterrorstring(e)
        print(error)
        return json.dumps({'status':'error','response':error},indent=2)
        
@app.route('/<id>/keypress/<int:keycode>', methods=['GET'])
def displaykeypress(id,keycode):
    #return f'{id} {keycode}'
    try:
        C__flaskdisplay(id=id).keypress(keycode)
        return json.dumps({'status':'ok','response':f'press {keycode} {chr(keycode)}'},indent=2)
    except Exception as e:
        error=geterrorstring(e)
        print(error)
        return json.dumps({'status':'error','response':error},indent=2)

@app.route('/<id>/status', methods=['GET'])
def displaystatus(id):
    try:
        s=C__flaskdisplay(id=id).status()
    except Exception as e:
        s=''
    return json.dumps({'status':'ok','response':s},indent=2)

@app.route('/<id>/command', methods=['GET'])
def displaycommand(id):
    command=request.args.get('k')
    #return f'{id} {keycode}'
    try:
        C__flaskdisplay(id=id).command(command)
        return json.dumps({'status':'ok','response':f'command {command}'},indent=2)
    except Exception as e:
        error=geterrorstring(e)
        print(error)
        return json.dumps({'status':'error','response':error},indent=2)
    

    
@app.route('/<id>/', methods=['GET'])
def display(id):
    #return f'{id} {keycode}'
    return render_template('display.htm')

@app.route('/<id>/image.jpg', methods=['GET'])
def get_image(id):
    # Replace 'path/to/your/image.jpg' with the path to the image file
    image_path = f'/dev/shm/flaskdisplay/{id}/image.jpg'
    return send_file(image_path, mimetype='image/jpeg')

@app.route('/<id>/poll', methods=['GET'])
def poll(id):
    # Replace 'path/to/your/image.jpg' with the path to the image file    
    try:
        return open(C__flaskdisplay(id=id).lastupdatef).read()
    except:
        return '{}'

def generate_time_image():
    # Create a blank 200x200 black image
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    # Get the current time in the desired format
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Set font type and scale
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color = (255, 255, 255)  # White color for the text
    thickness = 1

    # Calculate the size of the text
    text_size = cv2.getTextSize(current_time, font, font_scale, thickness)[0]

    # Calculate the text position to center it
    text_x = (image.shape[1] - text_size[0]) // 2
    text_y = (image.shape[0] + text_size[1]) // 2

    # Add the text to the image
    cv2.putText(image, current_time, (text_x, text_y), font, font_scale, color, thickness)

    return image

if __name__ == '__main__':
    try:
        port=int(sys.argv[1])
    except:
        port=5009
    app.run(host='0.0.0.0',port=int(port),debug=False)
