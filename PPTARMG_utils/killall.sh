  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)  

  cd /home/mvizn/Code/docker.mviznARMG_ppt

  echo clear all docker  
  docker stop $(docker ps -q)
  docker rm $(docker ps -aq)  

  echo docker compose down
  docker compose kill
  docker compose down 
