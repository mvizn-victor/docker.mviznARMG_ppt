# Usage:
# bash rsyncfromtodate.sh {startdate} {next date after enddate} {source path} {destination path}
# Source or destination path cannot be ./
# Example to rsync 7409 data that was only on 2021-12-12:
# bash rsyncfromtodate.sh 2021-12-12 2021-12-13	$ARMG/7409 /media/mvizn/RawData3

sleep 10

#src=/opt/captures
src=$3
#dest="$PWD"/captures
dest=$4
touch -d "$1" /tmp/startdate
touch -d "$2" /tmp/enddate
#find . -newer startdate -type f -print
cd "$src"

if [ ! -f $4/rsync.log ]
then
	touch $4/rsync.log
fi

echo "Rsync started at:" >> $4/rsync.log
date >> $4/rsync.log

#start_time=$SECONDS

while true
do
  start_time=$SECONDS
  find . -newer /tmp/startdate -type f -not -newer /tmp/enddate -type f -print | rsync -av --files-from=- . "$dest"

  elapsed=$(( SECONDS - start_time))
  eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')"
  echo "Rsync ended at:" >> $4/rsync.log
  date >> $4/rsync.log
  eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')" >> $4/rsync.log

  sleep 300
done


#elapsed=$(( SECONDS - start_time))
#eval "echo Elapsed time: $(date -ud "@$elapsed" +'$((%s/3600/24)) days %H hr %M min %S sec')"

#echo "Rsync ended at:" >> $4/rsync.log
#date >> $4/rsync.log
