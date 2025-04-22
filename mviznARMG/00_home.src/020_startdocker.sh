docker stop $(docker ps -aq) 

docker rm $(docker ps -aq)  

screen -dSm docker1 docker run --gpus all  -it --rm --name docker1 -p 9888:9888 -v /opt:/opt -v /dev/shm:/dev/shm -v /home/mvizn:/home/mvizn 617767309507.dkr.ecr.ap-southeast-1.amazonaws.com/mvizn/cudaopencv:11.1.1-cudnn8-opencv4.6-devel-ubuntu18.04 bash -c  '.  /home/mvizn/Code/mviznARMG/docker1/01_*'

screen -dSm docker2 docker run --gpus all -v /opt:/opt -v /dev/shm:/dev/shm -v /home/mvizn/.jupyter:/home/appuser/.jupyter -v /home/mvizn:/home/mvizn --net=host -it --rm --env="DISPLAY" --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw"   --name=detectron2 detectron2_repo_docker-detectron2 bash -c '.  /home/mvizn/Code/mviznARMG/docker2/02_*'
#--gpus '"device=1"'
