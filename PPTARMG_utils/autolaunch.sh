filename="/dev/shm/launched"
if [ -e "$filename" ]; then
  echo "File $filename exists."
else
  echo "File $filename does not exist."
  touch $filename
  export PYTHONPATH=.

  cd /home/mvizn/Code/docker.mviznARMG_ppt

  bash ~/PPTARMG_utils/killall.sh
  bash ~/PPTARMG_utils/runall.sh

fi
