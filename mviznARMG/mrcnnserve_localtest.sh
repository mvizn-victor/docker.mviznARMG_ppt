docker kill tf-docker
docker rm tf-docker
#docker run --gpus device=0 --name=tf-docker -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/mvizn/Code/mviznARMG
docker run --gpus device=0 --name=tf-docker -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/mvizn/Code/mviznARMG/mrcnn_serving_ready/serving_model,target=/models/mask -e MODEL_NAME=mask  -t tensorflow/serving:latest-gpu
