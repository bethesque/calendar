import subprocess
import time
import json
import socket
import os

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"
ALARM_FILES = ["audio/announcement.mp3", "audio/alarm.mp3"]
SILENCE_FILE = "audio/silence_5s.m4a"
DEFAULT_VOLUME = 50

# Note: You'll need to create a 10-second silent audio file named "silence_10s.m4a"
# You can create one with: ffmpeg -f lavfi -i "sine=frequency=0:duration=10" -c:a aac silence_10s.m4a

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
        print(f"mpv {ipc_socket} is already running")
        return None

    # Remove old socket if it exists
    if os.path.exists(ipc_socket):
        os.remove(ipc_socket)

    proc = subprocess.Popen([
        "mpv",
        "--idle=yes",
        "--no-video",
        f"--input-ipc-server={ipc_socket}",
        "--really-quiet"
    ])
    return proc

def start_mpv_2(ipc_socket):
    """Start mpv with IPC if not already running."""
    if is_mpv_running(ipc_socket):
        print(f"mpv {ipc_socket} is already running")
        return None

    # Remove old socket if it exists
    if os.path.exists(ipc_socket):
        os.remove(ipc_socket)

    proc = subprocess.Popen([
        "mpv",
        "--idle=yes",
        "--no-video",
        "--loop-playlist=inf",
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
    message = (json.dumps({"command": [cmd] + args}) + "\n").encode("utf-8")
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            print(f"Sending command to {ipc_socket}: {message}")
            s.connect(ipc_socket)
            s.sendall(message)
            

            response = b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b"\n" in chunk:
                    break

        decoded = response.decode("utf-8", errors="replace").strip()
        if decoded:
            print(f"mpv response ({ipc_socket}): {decoded}")
    except (ConnectionRefusedError, FileNotFoundError):
        print(f"mpv {ipc_socket} is not running or IPC socket missing")

def play_alarm(file_path):
    # Set playlist to loop infinitely
    send_command(ALARM_SOCKET, "set_property", ["loop-file", "inf"])
    send_command(ALARM_SOCKET, "loadfile", [file_path])

def create_announcement_playlist(announcement_file):
    """Create a looping playlist: announcement -> 10s silence -> repeat"""
    # Clear any existing playlist
    send_command(ANNOUNCEMENT_SOCKET, "playlist_clear")
    
    # Add announcement file
    send_command(ANNOUNCEMENT_SOCKET, "loadfile", [announcement_file, "append-play"])
    
    # Add silent audio file (you'll need to create a 10-second silent MP3)
    send_command(ANNOUNCEMENT_SOCKET, "loadfile", [SILENCE_FILE, "append-play"])
    
    # Set playlist to loop infinitely
    send_command(ANNOUNCEMENT_SOCKET, "set_property", ["loop-playlist", "inf"])

def set_volume(ipc_socket, vol):
    send_command(ipc_socket, "set_property", ["volume", vol])

  
# Example usage
if __name__ == "__main__":
    start_mpv(ALARM_SOCKET)
    start_mpv_2(ANNOUNCEMENT_SOCKET)

    if not wait_for_ipc(ALARM_SOCKET, timeout=20.0):
        print(f"Error: mpv alarm IPC socket at {ALARM_SOCKET} not ready")
        exit(1)

    if not wait_for_ipc(ANNOUNCEMENT_SOCKET, timeout=20.0):
        print(f"Error: mpv announcement IPC socket at {ANNOUNCEMENT_SOCKET} not ready")
        exit(1)        

    set_volume(ALARM_SOCKET, DEFAULT_VOLUME)    
    set_volume(ANNOUNCEMENT_SOCKET, DEFAULT_VOLUME)    
    
    # Play the alarm
    play_alarm(ALARM_FILES[1])

    # Start the looping announcement playlist
    create_announcement_playlist(ALARM_FILES[0])

    print("Done")