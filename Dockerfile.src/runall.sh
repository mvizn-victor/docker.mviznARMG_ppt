#ie15
# rm /dev/shm/VCMC/* and /dev/shm/cam*
# mkdir -p /opt/captures using user to prevent created with root permission

  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)
  export DISPLAY=$(cat ~/DISPLAY)
  cd /home/mvizn/Code/docker.mviznARMG_ppt
  bash ~/PPTARMG_utils/killall.sh

  rm /dev/shm/VCMC/*
  rm /dev/shm/cam*
  mkdir -p /opt/captures

  echo docker compose up
  if [ "$1" = "pull" ];then
    #docker pull gaseooo/detectron2:1.0.1
    docker pull ubuntu:24.04  # for flaskdisplay
    docker pull python:3.8-slim # for UI
    docker pull pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime  # for detectron
    docker pull pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime
    #docker pull nvidia/cuda:11.1.1-cudnn8-devel-ubuntu18.04
    docker pull ghcr.io/mvizn/mvizn-docker-images:4.11.0_cuda12.4.1-cudnn-devel-ubuntu22.04
    docker pull ghcr.io/mvizn/mvizn-docker-images:4.11.0_cuda12.4.1-cudnn-devel-ubuntu22.04-noAVX2
    exit
  elif [ "$1" = "build" ];then
    docker compose up --build --remove-orphans
    echo BUILD DONE
    bash ~/PPTARMG_utils/killall.sh
    exit
  else
    docker compose up --build --remove-orphans 2>&1 > /dev/null &
  fi
  echo sleep 3
  sleep 3
  echo "Closing existing firefox"
  xdotool search --onlyvisible --class firefox windowactivate
  # Close tabs one by one
  for i in {1..10}; do  # adjust 20 to a larger number if you want
      xdotool key ctrl+w
      sleep 0.1  # small delay to avoid overwhelming
  done
  xdotool search --onlyvisible --class firefox windowactivate
  # Close tabs one by one
  for i in {1..10}; do  # adjust 20 to a larger number if you want
      xdotool key ctrl+w
      sleep 0.1  # small delay to avoid overwhelming
  done
  killall firefox

  echo "Launching firefox"
  # Try launching Firefox in the background and suppressing output errors
  firefox http://localhost:5000/main https://localhost:8000 &>/dev/null &
  while ! window_id=$(xdotool search --onlyvisible --class "Firefox" 2>/dev/null); do
    sleep 0.5
  done
  xdotool windowmove "$window_id" 0 0
  xdotool windowsize "$window_id" 50% 100%  
