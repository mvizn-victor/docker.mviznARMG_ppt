#version:1
while true;do
	FILENAME=`date +%Y-%m-%d`/`date +%Y-%m-%d_%H-%M-%S.txt.gz`
	echo $FILENAME
	mkdir -p /opt/captures/psfaux/`date +%Y-%m-%d`
	ps faux|gzip > /opt/captures/psfaux/$FILENAME
	sleep 10
done
