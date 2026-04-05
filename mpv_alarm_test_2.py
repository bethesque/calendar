import subprocess
import time
import os

# Path to the FIFO
FIFO = "/tmp/mpvpipe"

# Path to your alarm file (can preload in /dev/shm if desired)
ALARM_FILE = "alarm.mp3"

# Ensure the FIFO exists
if not os.path.exists(FIFO):
    os.mkfifo(FIFO)

# Start mpv in idle mode
def start_mpv():
    try:
        return subprocess.Popen([
            "mpv",
            "--idle=yes",           # stay open when not playing
            "--no-video",           # audio only
            "--input-file=" + FIFO,
            "--really-quiet"        # suppress extra logs
        ])
    except Exception as e:
        print("Failed to start mpv:", e)
        return None

# Play a file instantly
def play_alarm(file_path=ALARM_FILE):
    with open(FIFO, "w") as fifo:
        fifo.write(f"loadfile {file_path}\n")

# Stop playback immediately
def stop_alarm():
    with open(FIFO, "w") as fifo:
        fifo.write("stop\n")

# Fade out over 'duration' seconds
def fade_out(duration=2.0, steps=10):
    step_time = duration / steps
    for vol in reversed(range(0, 101, 100 // steps)):
        with open(FIFO, "w") as fifo:
            fifo.write(f"set volume {vol}\n")
        time.sleep(step_time)
    stop_alarm()
    # Reset volume to 100% for next play
    with open(FIFO, "w") as fifo:
        fifo.write("set volume 100\n")

# Example usage
if __name__ == "__main__":
    # Start mpv if not already running
    mpv_proc = start_mpv()

    try:
        print("Playing alarm...")
        play_alarm()
        time.sleep(5)  # wait 5 seconds

        print("Fading out alarm...")
        fade_out(duration=3.0)

        print("Done")
    except BrokenPipeError:
        # If mpv crashed, restart and try again
        print("mpv crashed, restarting...")
        mpv_proc = start_mpv()
        play_alarm()