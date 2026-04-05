import subprocess
import time
import json
import socket
import os

IPC_SOCKET = "/tmp/mpv_socket"
ALARM_FILE = "alarm.mp3"

def is_mpv_running():
    """Return True if mpv IPC socket exists and is connectable."""
    if not os.path.exists(IPC_SOCKET):
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            s.connect(IPC_SOCKET)
        return True
    except (ConnectionRefusedError, FileNotFoundError, socket.timeout):
        return False

def start_mpv():
    """Start mpv with IPC if not already running."""
    if is_mpv_running():
        print("mpv is already running")
        return None

    # Remove old socket if it exists
    if os.path.exists(IPC_SOCKET):
        os.remove(IPC_SOCKET)

    proc = subprocess.Popen([
        "mpv",
        "--idle=yes",
        "--no-video",
        f"--input-ipc-server={IPC_SOCKET}",
        "--really-quiet"
    ])
    # Give mpv a moment to start and create the socket
    time.sleep(0.5)
    return proc

def wait_for_ipc(timeout=2.0):
    """Wait until mpv IPC socket exists and is connectable."""
    start = time.time()
    while True:
        if os.path.exists(IPC_SOCKET):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    s.connect(IPC_SOCKET)
                return True
            except (ConnectionRefusedError, socket.timeout):
                pass
        if time.time() - start > timeout:
            return False
        time.sleep(0.05)

def send_command(cmd, args=None):
    if args is None:
        args = []
    message = json.dumps({"command": [cmd] + args}) + "\n"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(IPC_SOCKET)
            s.sendall(message.encode("utf-8"))
    except (ConnectionRefusedError, FileNotFoundError):
        print("mpv is not running or IPC socket missing")

def play_alarm(file_path=ALARM_FILE):
    send_command("loadfile", [file_path])

def stop_alarm():
    send_command("stop")

def set_volume(vol):
    send_command("set_property", ["volume", vol])

def fade_out(duration=2.0, steps=10):
    step_time = duration / steps
    for vol in reversed(range(0, 101, 100 // steps)):
        set_volume(vol)
        time.sleep(step_time)
    stop_alarm()
    set_volume(100)  # reset volume

# Example usage
if __name__ == "__main__":
    mpv_proc = start_mpv()  # starts mpv if not running
    if not wait_for_ipc(timeout=10.0):
        print("Error: mpv IPC socket not ready")
        exit(1)    

    print("Playing alarm...")
    play_alarm()
    time.sleep(5)

    print("Fading out alarm...")
    fade_out(duration=3.0)

    print("Done")