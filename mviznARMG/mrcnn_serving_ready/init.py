import sys
sys.path.append('/home/mvizn/Code/mviznARMG/mrcnn_serving_ready')
from inferencing.saved_model_inference import detect_mask_single_image
import numpy as np
print(detect_mask_single_image(np.zeros((3,3,3),dtype=np.uint8)))