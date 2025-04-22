#version:1
#cd /mnt/NFSDIR/yardpmtextrecognition
#tensorflow_model_server --port=9000 --rest_api_port=9001 --model_name=AOCR --model_base_path=/home/mvizn/Code/mviznARMG/PMNRS/weights/exported
tensorflow_model_server --port=9000 --rest_api_port=9001 --model_name=AOCR --model_base_path=/home/mvizn/Code/mviznARMG/PMNRS/weights/aocr
