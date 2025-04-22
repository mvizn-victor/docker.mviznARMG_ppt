#!/usr/bin/env python3
import os
import sys
import time
import signal
from datetime import datetime

def print_usage():
    """Display usage instructions."""
    print("params: <log_file>")
    sys.exit(1)

T = time.time()

def main():
    global T

    # Parameter Validation
    if len(sys.argv) != 2:
        print_usage()

    log_file = sys.argv[1]
    print(f"Starting Smart Logger with log file '{log_file}'.")

    # Ensure no conflicting log files
    if not os.path.isabs(log_file):
        print("Error: Log file path must be absolute.")
        sys.exit(1)

    # Open stdin and log file in unbuffered mode
    sys.stdin = os.fdopen(sys.stdin.fileno(), 'rb', buffering=0)  # Unbuffered stdin
    log_fd = open(log_file, 'ab', buffering=0)  # Unbuffered log file

    # Trap SIGTERM and SIGINT for graceful shutdown
    def cleanup(signal_received, frame):
        print("Stopping Smart Logger. Goodbye!")
        log_fd.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Main loop to read stdin and write to log
    try:
        while True:
            line = sys.stdin.readline()  # Read binary line from stdin
            if not line:
                break  # Stop if stdin closes
            if time.time() - T > 0:
                T = time.time()
                line = ('LOGDT: ' + str(datetime.now()) + ' ').encode() + line
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
            log_fd.write(line)
            log_fd.flush()
            # Check if log file still exists
            if not os.path.exists(log_file):
                log_fd.close()
                open(log_file, 'wb').close()  # Recreate log file
                log_fd = open(log_file, 'ab', buffering=0)  # Reopen in unbuffered mode
    except KeyboardInterrupt:
        cleanup(None, None)
    finally:
        log_fd.close()

if __name__ == "__main__":
    main()

