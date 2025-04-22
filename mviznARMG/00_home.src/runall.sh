show=$1
export DISPLAY=$(cat ~/DISPLAY)
export PATH=/home/mvizn/bin:/home/mvizn/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin
bash ~/killall.sh
screen -dSm docker bash ~/020*
cd ~/Code/mviznARMG
. a
screen -dSm workflow bash /home/mvizn/Code/mviznARMG/run.sh main

