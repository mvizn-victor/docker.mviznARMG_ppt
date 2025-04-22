#!/usr/bin/env python3
#rotatelog.py
import os
import shutil
import gzip
import sys

def rotate_logs(log_file,log_folder):
    """Rotate and gzip the log file with numerical suffixes."""
    # Ensure the file exists
    if log_folder=='':
        log_folder = os.path.dirname(log_file)
    if not os.path.exists(log_file):
        print(f"Log file '{log_file}' does not exist.")
        return
    base=os.path.basename(log_file)
    # Rotate existing files: .3.gz -> .4.gz, .2.gz -> .3.gz, etc.
    for i in range(MAX_ROTATIONS-1, 0, -1):
        old_file = f"{log_folder}/{base}.{i}"
        new_file = f"{log_folder}/{base}.{i+1}"
        if os.path.exists(old_file):
            os.rename(old_file, new_file)
            print(f"Rotated: {old_file} -> {new_file}")
    
    os.rename(log_file, f"{log_folder}/{base}.1")
    
try:
    assert len(sys.argv) >= 4
    MAX_ROTATIONS = int(sys.argv[1])  # Keep up to 4 rotated log files (e.g., .1.gz, .2.gz, ...)
    log_folder = sys.argv[2]
    log_files = sys.argv[3:]
    for log_file in log_files:
        rotate_logs(log_file,log_folder)
except:
    #raise
    """Display usage instructions."""
    print("params: <max_rotations> <log_folder> <log_file1> <log_file2> ...")
    sys.exit(1)
