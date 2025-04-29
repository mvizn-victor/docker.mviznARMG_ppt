cd ~/Code/docker.mviznARMG_ppt
echo '>>>> do apt install, enter vapc password:'
bash aptinstall.sh
bash 01_*.sh
if [ ! -e ~/PPTARMG_config ]; then
    bash 02_*.sh
fi
touch /tmp/launched
crontab PPTARMG_utils/cron.txt
bash runall.sh pull
bash runall.sh build
