#run.sh
export PYTHONPATH=.
while true;do
    echo run loop
	stdbuf -oL python3 -u _pythonloop/s1/0.py
	sleep 1
done
