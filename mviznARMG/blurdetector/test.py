from blurdetector.getblurryscore import *
import cv2
im=cv2.imread('CLPS/sample/2020-01-09/15-00-29/2020-01-09_15-01-03_tl20b.jpg')
print(getblurryscore(im))
