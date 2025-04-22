ip_s47="10.66.203.47"
ip_s36="10.66.203.36"
ip_7409="10.140.98.157";
ip_8201="10.140.51.93";
import os
ip_plc=os.popen('grep 10.148 config/config.py').read().split("'")[1].split("'")[0]
ip_lcms=".".join(ip_plc.split(".")[:3])+".99"
cmd=f"""
sudo ufw --force disable
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from {ip_8201} to any port 22
sudo ufw allow from {ip_8201} to any port 5900
sudo ufw allow from {ip_7409} to any port 22
sudo ufw allow from {ip_7409} to any port 5900
sudo ufw allow from {ip_s47} to any port 22
sudo ufw allow from {ip_s47} to any port 5900
sudo ufw allow from {ip_s36} to any port 22
sudo ufw allow from {ip_s36} to any port 5900
sudo ufw allow from {ip_lcms} to any port 22
sudo ufw allow from {ip_lcms} to any port 5900
sudo ufw --force enable
"""
print(cmd)
os.system(cmd)
