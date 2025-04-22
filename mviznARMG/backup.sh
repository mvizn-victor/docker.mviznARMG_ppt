set -e
mkdir -p $1
#tar -cf /tmp/1.tar --exclude weights --exclude sample --exclude .git *;tar -xf /tmp/1.tar -C $1
rsync --no-p --exclude '/config/' --exclude '/configv1/' --exclude weights/ --exclude sample/ --exclude .git/ --exclude '*model*' --exclude Mask_RCNN --exclude EAST --exclude detectron2_repo -av * $1
