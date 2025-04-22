#version: 1.0.0

import torch
import timm
from timm.data.transforms_factory import create_transform
from timm.data import resolve_data_config
from PIL import Image
import os

def cv2_to_pil(cv2_image):
    from PIL import Image
    # Convert from BGR to RGB
    cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    # Convert the OpenCV image to a PIL image
    pil_image = Image.fromarray(cv2_image_rgb)
    return pil_image

class EfficientNet():
    def __init__(self,model_chkpoint = '/mnt/NFSDIR2/TLD-Project-Data/inception/TLD_Inception_2024-10-13b/timm_outs/output/train/20241021-030703-efficientnet_b0-224/model_best.pth.tar',labelsfile=None):
        if labelsfile is None:
            my_class_map = {'C1': 0, 'C2': 1, 'C3': 2, 'C4': 3, 'C5': 4, 'C6': 5, 'C9': 6, 'C11': 7, 'C12': 8, 'C13': 9, 'C14': 10, 'C15': 11, 'C16': 12, 'C17': 13, 'C18': 14, 'F1': 15, 'F1a': 16, 'F1b': 17, 'F2': 18, 'F3': 19, 'F4': 20, 'M1': 21, 'M2': 22, 'M3': 23, 'M4': 24, 'M5': 25, 'S1': 26, 'S2': 27, 'S3': 28, 'S4': 29, 'S5': 30, 'S6': 31, 'S7': 32, 'S8': 33, 'S9': 34, 'S9a': 35, 'S10': 36, 'S11': 37, 'S12': 38, 'S13': 39, 'S14': 40, 'S14a': 41, 'S15': 42, 'S16': 43, 'S17': 44, 'S18': 45, 'S19': 46, 'S20': 47, 'S21': 48, 'S22': 49, 'S23': 50, 'S24': 51, 'S25': 52, 'S26': 53, 'S27': 54, 'S28': 55}
            self.classes = list(my_class_map.keys())
        else:            
            if not os.path.isfile(filename):
                print('File does not exist.')
            else:
                # Open the file and read its content.
                with open(filename) as f:
                    self.classes = f.read().splitlines()

        model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=56)
        checkpoint = torch.load(model_chkpoint)
        model.load_state_dict(checkpoint['state_dict'])
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model=model.to(self.device)

    def infer(self,cv2image=None):
        image = cv2_to_pil(cv2image)
        self.model.eval()

        config = resolve_data_config({}, model=self.model)
        timm_transform = create_transform(**config)
        
        image_tensor = timm_transform(image).unsqueeze(0)
        #image_tensor.size()
        image_tensor = image_tensor.to(self.device)
        
        # Step 5: Perform inference
        with torch.no_grad():  # Disable gradient computation for inference
            output = self.model(image_tensor)
        
        # Step 6: Get the predicted class
        # If it's a classification task, the output will be logits, so we apply softmax
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
        # Get the index of the highest probability class
        max_prob = probabilities.max().item()
        predicted_class = probabilities.argmax().item()

        return (self.classes[predicted_class],max_prob)
