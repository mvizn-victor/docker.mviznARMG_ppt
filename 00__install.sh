cd ~/Code/docker.mviznARMG_ppt
echo $DISPLAY > ~/DISPLAY

echo "checking"
# Get the total size in kilobytes (1K-blocks) from df
total_kb=$(df --output=size /opt| tail -1)

# Convert 1.5TB to kilobytes (1.5 * 1024 * 1024 * 1024)
threshold_kb=$((1.5 * 1024 * 1024 * 1024))

if [ "$total_kb" -lt "$threshold_kb" ]; then
    echo "Total space of /opt is less than 1.5TB, raid probably not mounted!"
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
