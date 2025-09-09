docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi -f $(docker images -q)
docker volume rm $(docker volume ls -q)
docker network rm $(docker network ls | grep -v "bridge\|host\|none" | awk '{print $1}')
docker system prune -a --volumes -f