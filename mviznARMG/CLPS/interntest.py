import subprocess

def main():
    # Command to open a new GNOME Terminal with a specific title
    terminal_command = 'gnome-terminal --title=Video'

    # Command to change directory to the specified path
    cd_command = 'cd ~/Code/mviznARMG/CLPS/'

    # Command to open the video file using ffplay with looping every 1 second
    open_video_command = 'ffplay -loop 0 ts4xb-16_40.mp4'

    # Combine commands using && to run them sequentially in the same terminal
    final_command = f"{terminal_command} -- bash -c '{cd_command} && {open_video_command}; bash'"

    # Run the final command using subprocess
    subprocess.run(final_command, shell=True)

if __name__ == "__main__":
    main()
