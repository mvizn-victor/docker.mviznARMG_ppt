#version:ehz
#ehz:
#  added DISPLAY which will be present when first ran after calibration
if pgrep -f Processor/workflow.py
then
	exit
fi

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
. a
bash killall.sh
python Processor/workflow.py $1
bash killall.sh
