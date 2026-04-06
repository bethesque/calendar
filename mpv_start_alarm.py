import subprocess
import time
import json
import socket
import os

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"
ALARM_FILES = ["announcement.mp3", "alarm.mp3"]
DEFAULT_VOLUME = 50

def is_mpv_running(ipc_socket):
    """Return True if mpv IPC socket exists and is connectable."""
    if not os.path.exists(ipc_socket):
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            s.connect(ipc_socket)
        return True
    except (ConnectionRefusedError, FileNotFoundError, socket.timeout):
        return False

def start_mpv(ipc_socket):
    """Start mpv with IPC if not already running."""
    if is_mpv_running(ipc_socket):
        print("mpv is already running")
        return None

    # Remove old socket if it exists
    if os.path.exists(ipc_socket):
        os.remove(ipc_socket)

    proc = subprocess.Popen([
        "mpv",
        "--idle=yes",
        "--no-video",
        "--loop-file=inf",
        f"--input-ipc-server={ipc_socket}",
        "--really-quiet"
    ])
    return proc

def wait_for_ipc(ipc_socket, timeout=2.0):
    """Wait until mpv IPC socket exists and is connectable."""
    start = time.time()
    while True:
        if os.path.exists(ipc_socket):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    s.connect(ipc_socket)
                return True
            except (ConnectionRefusedError, socket.timeout):
                pass
        if time.time() - start > timeout:
            return False
        time.sleep(0.05)

def send_command(ipc_socket, cmd, args=None):
    if args is None:
        args = []
    message = json.dumps({"command": [cmd] + args}) + "\n"
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(ipc_socket)
            s.sendall(message.encode("utf-8"))
    except (ConnectionRefusedError, FileNotFoundError):
        print("mpv is not running or IPC socket missing")

def play_alarm(file_path):
    send_command(ALARM_SOCKET, "loadfile", [file_path])

def play_announcement(file_path):
    send_command(ANNOUNCEMENT_SOCKET, "loadfile", [file_path])    

def stop_alarm(ipc_socket):
    send_command(ipc_socket, "stop")

def set_volume(ipc_socket, vol):
    send_command(ipc_socket, "set_property", ["volume", vol])

  
# Example usage
if __name__ == "__main__":
    start_mpv(ALARM_SOCKET)
    start_mpv(ANNOUNCEMENT_SOCKET)

    if not wait_for_ipc(ALARM_SOCKET, timeout=10.0):
        print("Error: mpv alarm IPC socket not ready")
        exit(1)

    if not wait_for_ipc(ANNOUNCEMENT_SOCKET, timeout=10.0):
        print("Error: mpv announcement IPC socket not ready")
        exit(1)        

    set_volume(ALARM_SOCKET, DEFAULT_VOLUME)    
    set_volume(ANNOUNCEMENT_SOCKET, DEFAULT_VOLUME)    

    play_alarm(ALARM_FILES[1])
    play_announcement(ALARM_FILES[0])

    print("Done")