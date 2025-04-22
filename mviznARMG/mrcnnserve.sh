docker kill tf-docker
docker rm tf-docker
docker run --gpus device=1 --name=tf-docker -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/mvizn/Code/mviznARMG/mrcnn_serving_ready/serving_model,target=/models/mask -e MODEL_NAME=mask  -t tensorflow/serving:latest-gpu --per_process_gpu_memory_fraction=0.25  >/dev/null 2>&1 &
#--per_process_gpu_memory_fraction=1 
python mrcnn_serving_ready/init.py
