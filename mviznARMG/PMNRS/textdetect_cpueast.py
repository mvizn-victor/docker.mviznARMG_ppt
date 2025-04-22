from datetime import datetime
import cv2
import base64
import math
import requests

net = cv2.dnn.readNet('/home/mvizn/Code/mviznARMG/PMNRS/weights/frozen_east_text_detection.pb')


def decode(scores, geometry, scoreThresh):
    detections = []
    confidences = []

    ############ CHECK DIMENSIONS AND SHAPES OF geometry AND scores ############
    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):

        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]

            # If score is lower than threshold score, move to next x
            if(score < scoreThresh):
                continue

            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]

            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0],  sinA * w + offset[1])
            center = (0.5*(p1[0]+p3[0]), 0.5*(p1[1]+p3[1]))
            detections.append((center, (w,h), -1*angle * 180.0 / math.pi))
            confidences.append(float(score))

    # Return detections and confidences
    return [detections, confidences]


def gettextboxes(frame):
    inpWidth=320;inpHeight=320
    h,w,d=frame.shape
    import time
    T=[]
    T.append(time.time())
    blob = cv2.dnn.blobFromImage(frame, 1.0, (inpWidth, inpHeight), (123.68, 116.78, 103.94), True, False)        
    T.append(time.time())
    print(len(T)-1,T[-1]-T[-2])
    outputLayers = []
    outputLayers.append("feature_fusion/Conv_7/Sigmoid")
    outputLayers.append("feature_fusion/concat_3")
    net.setInput(blob)
    T.append(time.time())
    print(len(T)-1,T[-1]-T[-2])
    output = net.forward(outputLayers)
    T.append(time.time())
    print(len(T)-1,T[-1]-T[-2])
    scores = output[0]
    geometry = output[1]
    [boxes, confidences] = decode(scores, geometry, 0.5)
    T.append(time.time())
    print(len(T)-1,T[-1]-T[-2])
    indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, 0.5, 0.4)
    print(len(T)-1,T[-1]-T[-2])
    outboxes=[]
    for i in indices:
        vertices=cv2.boxPoints(boxes[i[0]])
        x1=max(int(min(vertices[:,0])/inpWidth*w)-2,0)
        y1=max(int(min(vertices[:,1])/inpHeight*h)-2,0)
        x2=int(max(vertices[:,0])/inpWidth*w)+2
        y2=int(max(vertices[:,1])/inpHeight*h)+2
        outboxes.append((x1,y1,x2,y2))
        #outboxes.append(frame[y1:y2, x1:x2])
    print(len(T)-1,T[-1]-T[-2])
        
    return outboxes

def gettextpolygon(frame):
    inpWidth=320;inpHeight=320
    h,w,d=frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1.0, (inpWidth, inpHeight), (123.68, 116.78, 103.94), True, False)
    outputLayers = []
    outputLayers.append("feature_fusion/Conv_7/Sigmoid")
    outputLayers.append("feature_fusion/concat_3")
    net.setInput(blob)
    output = net.forward(outputLayers)

    scores = output[0]
    geometry = output[1]
    [boxes, confidences] = decode(scores, geometry, 0.5)
    indices = cv2.dnn.NMSBoxesRotated(boxes, confidences, 0.5, 0.4)
    outboxes=[]
    for i in indices:
        vertices=cv2.boxPoints(boxes[i[0]])
        vertices[:,0]=vertices[:,0]/inpWidth*w
        vertices[:,1]=vertices[:,1]/inpHeight*h
        outboxes.append(vertices)
        #outboxes.append(frame[y1:y2, x1:x2])
    return outboxes


def doOCR(inframe, outboxes, outframe, x0, y0,text=None):
    for x1,y1,x2,y2 in outboxes:
        image = inframe[y1:y2, x1:x2]
        # tf serving url
        retval, buffer = cv2.imencode('.jpg', image)
        jpg_as_text = base64.b64encode(buffer).decode('utf8')
        url = "http://localhost:9001/v1/models/AOCR:predict"

        r = requests.post(url=url, json={
            "signature_name": "serving_default",
            "inputs": {
                "input": {"b64": jpg_as_text}
            }
        })
        cv2.rectangle(outframe, (x0+x1, y0+y1), (x0+x2, y0+y2), (244, 226, 66), 1)
        if text is None:
            json = r.json()
            #text = f"{json['outputs']['output']}({json['outputs']['probability']:.3g})"
            #if json['outputs']['probability']>=0.8:
            if json['outputs']['probability'] >= 0.8:
                text=json['outputs']['output']
                #print(text)
            else:
                text=''
        cv2.putText(outframe, text, (x0 + x1, y0 + y1), cv2.FONT_HERSHEY_DUPLEX, 1,
                    (244, 66, 206))
        #print(datetime.now(),text)
        return text
        #print(r.json()['outputs']['probability'], r.json()['outputs']['output'])
