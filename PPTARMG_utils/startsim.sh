bash ~/PPTARMG_utils/runall.sh
touch /dev/shm/simARMG2
echo start simtcds
bash ~/PPTARMG_utils/simtcds.sh
echo wait 40 seconds
for i in {1..40};do
	echo $i
	sleep 1
done
echo start simclps
bash ~/PPTARMG_utils/simclps.sh
echo wait 40 seconds
for i in {1..40};do
	echo $i
	sleep 1
done
echo endsim
bash ~/PPTARMG_utils/endsim.sh