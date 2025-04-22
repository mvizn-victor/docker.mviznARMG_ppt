from config.config import *
import numpy as np
while True:
    x=np.zeros((1280,720,3),dtype=np.uint8)
    assignimage(x,x)
    #cv2.resize(x,(100,100))
