from cleanvision.issue_managers.image_property import BlurrinessProperty
import cv2
from PIL import Image
import numpy as np
def cv2_to_pil(cv2_image):
    # Convert from BGR to RGB
    cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    # Convert the OpenCV image to a PIL image
    pil_image = Image.fromarray(cv2_image_rgb)
    return pil_image
def getblurryscore(cv2_image):
    pilim=cv2_to_pil(cv2_image)
    class G:
        pass
    x=G()
    x.max_resolution=64
    x.name='blurriness'
    blur_score=BlurrinessProperty.calculate(x,pilim)[x.name]
    blur_score = 1 - np.exp(-1 * blur_score * 0.01)
    return int(round(255*blur_score))
