set -e
mkdir -p "$1"
#tar -cf /tmp/1.tar --exclude weights --exclude sample --exclude .git *;tar -xf /tmp/1.tar -C $1
#rsync --exclude config/ --exclude weights/ --exclude sample/ --exclude .git/ --exclude '*model*' -av * $1
rsync --no-p --exclude 'version_all.txt' --exclude '/config/' --exclude '/configv1/' --exclude .git/ -av * "$1"
