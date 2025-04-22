set -e
mkdir -p $1
rsync -av /tmp/armglog.last/ $1
