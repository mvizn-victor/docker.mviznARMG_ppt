#ie15
#  smarter raidmounted check

cd ~/Code/docker.mviznARMG_ppt
echo $DISPLAY > ~/DISPLAY

raidmounted=$(df /opt|awk 'END{print($NF!="/")}')
echo "raidmounted:" $raidmounted
if [ "$raidmounted" -eq "0" ]; then
    echo "raid not mounted!"
    read -p "Do you want to proceed? Type 'yes' to continue: " user_input
    if [ "$user_input" != "yes" ]; then
        echo "Exiting."
        exit 1
    fi
fi

echo Now doing apt install, enter vapc password:
bash aptinstall.sh
bash 01_*.sh
bash 02_*.sh
touch /dev/shm/launched
crontab PPTARMG_utils/cron.txt
bash runall.sh pull
bash runall.sh build
