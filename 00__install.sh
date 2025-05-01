cd ~/Code/docker.mviznARMG_ppt
echo $DISPLAY > ~/DISPLAY
echo First check that raid is mounted already?
echo Now doing apt install, enter vapc password:
bash aptinstall.sh
bash 01_*.sh
bash 02_*.sh
touch /tmp/launched
crontab PPTARMG_utils/cron.txt
bash runall.sh pull
bash runall.sh build
