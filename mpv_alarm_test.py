import subprocess
import time
import json
import socket
import os

MPV_SOCKET = "/tmp/mpv_alarm.sock"
AUDIO_FILE = "alarm.mp3"

def send_command(command):
    """Send a JSON command to mpv via IPC socket"""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(MPV_SOCKET)
        s.send((json.dumps(command) + "\n").encode())

# Ensure old socket is removed
if os.path.exists(MPV_SOCKET):
    os.remove(MPV_SOCKET)

# Start mpv
mpv_process = subprocess.Popen([
    "mpv",
    "--no-video",
    f"--input-ipc-server={MPV_SOCKET}",
    AUDIO_FILE
])

# Wait for mpv to start and create socket
for _ in range(50):
    if os.path.exists(MPV_SOCKET):
        break
    time.sleep(0.1)

# Let it play for 10 seconds
time.sleep(10)

# Fade out (from 100 → 0)
steps = 20
for i in range(steps, -1, -1):
    volume = int(100 * i / steps)
    send_command({
        "command": ["set_property", "volume", volume]
    })
    time.sleep(0.15)

# Stop playback
send_command({
    "command": ["quit"]
})

# Wait for process to exit
mpv_process.wait()
