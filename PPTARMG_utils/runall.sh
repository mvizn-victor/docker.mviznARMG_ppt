  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)
  cd /home/mvizn/Code/docker.mviznARMG_ppt
  bash ~/PPTARMG_utils/killall.sh

  echo docker compose up
  if [ "$1" = "pull" ];then
    #docker pull gaseooo/detectron2:1.0.1
    docker pull ubuntu:24.04  # for flaskdisplay
    docker pull pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime  # for detectron
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
  echo try firefox with DISPLAY=:0 and keep incrementing until success
  s=0  # Start with DISPLAY=:0
  while true; do
      export DISPLAY=":$s"
      echo "Trying DISPLAY=$DISPLAY"
      xdotool search --onlyvisible --class firefox windowactivate
 
      # Close tabs one by one
      for i in {1..20}; do  # adjust 20 to a larger number if you want
          xdotool key ctrl+w
          sleep 0.1  # small delay to avoid overwhelming
      done
      # Try launching Firefox in the background and suppressing output errors
      firefox http://localhost:5000/main https://localhost:8000 &>/dev/null &
      pid=$!

      # Wait a few seconds to check if Firefox is running successfully
      sleep 3

      # Check if the process is still running
      if ps -p $pid > /dev/null; then
          echo "Firefox started successfully on DISPLAY=$DISPLAY"
          break
      else
          echo "Firefox failed on DISPLAY=$DISPLAY, trying next..."
          s=$((s + 1))
      fi
  done
