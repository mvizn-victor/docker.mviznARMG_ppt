import cv2
import sys
numbins=1280//64
cap=cv2.VideoCapture(sys.argv[1])
while True:
    ret,frame=cap.read()
    height,width=frame.shape[:2]
    for bin in range(numbins):
        x=1280*bin//numbins
        cv2.line(frame, (x, 0), (x, height), (0, 0, 255), 2)
        cv2.putText(frame, str(bin), (x,100), 0, 1, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow('',frame)
    c=cv2.waitKey(0)
    if c==ord('q'):
        break

