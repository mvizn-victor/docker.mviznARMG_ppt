#run.sh
export PYTHONPATH=.
cd /mviznARMG
while true;do
    echo run loop
	stdbuf -oL python3 -u _pythonloop/s2/0.py
	sleep 1
done
