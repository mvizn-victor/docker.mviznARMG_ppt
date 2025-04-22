import os
import subprocess
import time
import sys

# Change the directory
os.chdir(os.path.expanduser("~/Code/mviznARMG"))

# Install dependencies
subprocess.run(["pip3", "install", "torch"])
subprocess.run(["pip3", "install", "torchvision"])
subprocess.run(["pip3", "install", "git+https://github.com/facebookresearch/detectron2.git"])
subprocess.run(["pip3", "install", "point-rend"])

# Execute the commands
commands = [
    "rm ~/DISPLAY",
    "cd ~/Code/mviznARMG",
    "killall run.sh",
    "bash killall.sh",
    "pkill -f workflow",
    "rsync -av configsample/ config",
    ". a"
]

for command in commands:
    subprocess.call(command, shell=True)
    time.sleep(0.1)  # Add a small delay to ensure commands are executed in order

gnome_commands = [
    ("maskrcnn", "CLPS/clps_maskrcnn_loop.py"),
    ("tfserve", "tfserve.sh"),
    ("textboxdetector", "PMNRS/textboxdetector.py"),
    ("hncdstopyolo", "HNCDS/hncdstopyolo.py"),
    ("hncdsinception", "HNCDS/hncdsinception.py"),
    ("hncdssideyolo", "HNCDS/hncdssideyolo.py"),
    ("clpstcds.py", "st_clps_tcds.sh"),
    ("hncdstop.py", "HNCDS/st_hncdstop.py"),
    ("hncdsside.py", "HNCDS/st_hncdsside.py"),
    ("pmnrstop.py", "PMNRS/st_pmnrstop.py")
]

python_executable = sys.executable

for title, script in gnome_commands:
    script_path = os.path.join(os.getcwd(), script)
    if script.endswith(".py"):
        command = f"gnome-terminal --title={title} -- bash -c 'cd {os.path.dirname(script_path)}; {python_executable} {script_path}; echo {title}; bash'"
    else:
        command = f"gnome-terminal --title={title} -- bash -c 'cd {os.path.dirname(script_path)}; bash {script_path}; echo {title}; bash'"
    subprocess.call(command, shell=True)
    time.sleep(5)  # Add a delay between gnome-terminal commands

time.sleep(2)  # Add a final delay