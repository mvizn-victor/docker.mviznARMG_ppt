#version:1
src=/opt/captures
dest="$PWD"/captures
touch -d "$1" /tmp/startdate
#find . -newer startdate -type f -print
cd "$src"
while true;do
  find . -newer /tmp/startdate -type f -print | rsync --progress -av --files-from=- . "$dest"
  sleep 300
done
