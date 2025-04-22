rm /dev/shm/s1.log
rm /dev/shm/s2.log
find . -name '.*swp'|xargs rm
screen -XS s1 quit
screen -XS s2 quit
screen -dSm s1 docker exec -it mvizn_pptarmg bash _pythonloop/s1/run.sh
screen -S s1 -X screen bash -c 'cd mviznARMG/_pythonloop/s1;vim -p 1.py /dev/shm/s1.log'
screen -dSm s2 docker exec -it mvizn_pptarmg_detectron bash /mviznARMG/_pythonloop/s2/run.sh
screen -S s2 -X screen bash -c 'cd mviznARMG/_pythonloop/s2;vim -p 1.py 2.py /dev/shm/s2.log'
screen -dr $1
