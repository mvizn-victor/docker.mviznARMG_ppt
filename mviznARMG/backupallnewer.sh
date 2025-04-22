src="$PWD"
dest="$2"
touch -d "$1" /tmp/startdate
#find . -newer startdate -type f -print
cd "$src"
mkdir -p "$dest"
find . -newer /tmp/startdate -type f -print |grep -v '/config/'| rsync --progress -av --files-from=- . "$dest"
