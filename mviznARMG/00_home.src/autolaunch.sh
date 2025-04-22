filename="/tmp/launched"
if [ -e "$filename" ]; then
  echo "File $filename exists."
else
  echo "File $filename does not exist."
  touch $filename
  bash runall0.sh 2>&1 > /tmp/log
  sleep 10
  killall firefox
fi
