#version:ehz
#ehz:
#  exit if run.sh already running
#  exit if ~/DISPLAY not present and $DISPLAY not set
if test -f ~/DISPLAY
then
	. ~/DISPLAY
else
	if test -z $DISPLAY
	then
		exit
	else
		echo export DISPLAY=$DISPLAY > ~/DISPLAY
	fi
fi

cd ~/Code/mviznARMG
#procs run
N=$(python3 countproc.py run.sh)
N2=$(python3 countproc.py /run.sh)
if test $N -ge 2
then
	if [[ $0 =~ / ]]
	then
		echo 'running from cron but run.sh already run. exiting'
		exit
	else
		if test $N2 -ge 1
		then
			echo 'killing run.sh from screen'
			bash ~/Code/mviznARMG/killall.sh
			pkill -f /run.sh
			sleep 1
		else
			echo 'another terminal running run.sh. exiting'
			exit
		fi
	fi
fi
. a
touch /tmp/startrun2
while true;do
    if [ -f /tmp/startrun2 ];then
        rm /tmp/startrun2
        if ! pgrep -f run2.sh;then
            echo run run2
            bash run2.sh $1
        fi
    fi
    sleep 1
    echo touch /tmp/startrun2 to restart
done
