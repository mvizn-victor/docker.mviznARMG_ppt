#version:ehz
#ehz:
#  to be run from cron to run run.sh in screen if not already run
#  must already have ran before from UI terminal (presence of ~DISPLAY file)
if pgrep -f run.sh
then
	exit
fi
if test -f ~/DISPLAY
then
	. ~/DISPLAY
else
	exit
fi
screen -dSm workflow bash /home/mvizn/Code/mviznARMG/run.sh main 
