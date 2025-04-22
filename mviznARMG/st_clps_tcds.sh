while true;
do
    . a
    if python CLPS/st_clps.py;then echo;else echo CLPS FAIL;fi
    if python TCDS/st_tcds.py;then echo;else echo TCDS FAIL;fi
done
