#version:1
import cv2
import numpy as np
class Inception:
    def __init__(self,pbfile,labelsfile=None):
        if labelsfile is None:
            labelsfile=pbfile[:-3]+'.labels'
        self.net=cv2.dnn.readNet(pbfile)
        self.classes=open(labelsfile).read().strip().split()
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        tmp = self.net.getLayerNames()    
        self.ln=[]
        for i in self.net.getUnconnectedOutLayers():
            self.ln.append(tmp[i[0]-1]) 
    def infer(self,frame):
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (299, 299),
                swapRB=True, crop=False)
        self.net.setInput(blob)
        self.layerOutputs = self.net.forward(self.ln)
        res = np.squeeze(self.layerOutputs)
        i = np.argmax(np.squeeze(self.layerOutputs))
        return self.classes[i],res[i]
class YOLO:
    def __init__(self,weightsfile,cfgfile=None,namesfile=None,size=None):
        if cfgfile is None:
            cfgfile=weightsfile[:-len('.weights')]+'.cfg'            
        if namesfile is None:
            namesfile=weightsfile[:-len('.weights')]+'.names'
        cfg=dict()
        for line in open(cfgfile):
            if '#' in line:continue
            try:
                k,v=line.strip().split('=')[:2]
                cfg[k]=v
            except:
                pass
        if size is None:
            size=(int(cfg['width']),int(cfg['height']))
        self.net=cv2.dnn.readNet(weightsfile, cfgfile)
        self.classes=open(namesfile).read().strip().split()
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(size=size, scale=1/255)
    def infer(self, frame, CONFIDENCE_THRESHOLD=0.2, NMS_THRESHOLD=0.4):
        classes, scores, boxes = self.model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        classes = list(self.classes[i[0]] for i in classes)
        scores = list(score[0] for score in scores)
        return classes, scores, boxes
    def inferold(self, frame, thresh=0.2):
        classes, scores, boxes = self.infer(frame, thresh)
        results = []
        for (classid, score, box) in zip(classes, scores, boxes):
            result=['',0,[0,0,0,0]]
            result[0]=classid
            result[1]=score
            box[0]=box[0]+box[2]/2
            box[1]=box[1]+box[3]/2
            result[2]=box
            results.append(result)
        return results

