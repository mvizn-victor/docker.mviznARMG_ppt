cd ~
bash 020*.sh
sleep 10;
cd ~/Code/mviznARMG
. a
screen -S st_clps -X quit
screen -S st_tcds -X quit
screen -S st_hncdst -X quit
screen -S st_hncdss -X quit
screen -S st_pmnrs -X quit
screen -dSm st_clps bash -c 'while true;do python3 CLPS/st_clps.py ;sleep 1;done'
screen -dSm st_tcds bash -c 'while true;do python3 TCDS/st_tcds.py ;sleep 1;done'
screen -dSm st_hncdsside python3 HNCDS/st_hncdsside.py 
screen -dSm st_hncdstop python3 HNCDS/st_hncdstop.py 
screen -L -Logfile /opt/st_pmnrstop.log -dSm st_pmnrstop python3 PMNRS/st_pmnrstop.py 
