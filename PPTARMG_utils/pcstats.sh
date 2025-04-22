#version: ic04
#ib14
#  ps faux, nvidia-smi, df -h, du -sh /dev/shm/*/
#ic04
#  nvidia-smi full
YMDHMS=$(date +"%Y-%m-%d_%H-%M-%S")
YMD=$(date +"%Y-%m-%d")
H=$(date +"%H")
folder="/opt/captures/pcstats/$YMD/$H"
mkdir -p $folder
ps faux > "$folder/${YMDHMS}_psfaux.txt"
nvidia-smi --query-gpu=name,utilization.gpu,memory.total,memory.used,memory.free,power.draw,power.limit,temperature.gpu --format=csv > "$folder/${YMDHMS}_nvidia-smi.txt"
nvidia-smi > "$folder/${YMDHMS}_nvidia-smi-full.txt"
df -h > "$folder/${YMDHMS}_df-h.txt"
du -sh /dev/shm/*/ > "$folder/${YMDHMS}_dudevshm.txt"
