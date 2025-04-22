#version:1
T=$1
CRANE=$2
DATE=$3
for i in $(seq $T -1 0);do
    echo rsync in $i seconds
    sleep 1
done
cd /media/mvizn/*/ARMG/$CRANE && echo copying && bash ~/Code/mviznARMG/rsyncfromdate.sh $DATE
