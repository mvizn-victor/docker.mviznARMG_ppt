touch /dev/shm/simARMG2
bash ~/PPTARMG_utils/runall.sh
for j in {1..99999};do
    echo start simtcds
    bash ~/PPTARMG_utils/simtcds.sh
    echo wait 40 seconds
    for i in {1..40};do
        echo tcds $i
        sleep 1
    done
    echo start simclps
    bash ~/PPTARMG_utils/simclps.sh
    echo wait 40 seconds
    for i in {1..40};do
        echo clps $i
        sleep 1
    done
    echo endsim
done
bash ~/PPTARMG_utils/endsim.sh
