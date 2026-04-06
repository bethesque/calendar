import subprocess
import time
import json
import socket
import os

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"

ALARM_FILE = "audio/alarm.mp3"
ANNOUNCEMENT_FILE = "audio/announcement.mp3"
SILENCE_FILE = "audio/silence_5s.m4a"

DEFAULT_VOLUME = 50

# Note: You'll need to create a 10-second silent audio file named "silence_10s.m4a"
# You can create one with: ffmpeg -f lavfi -i "sine=frequency=0:duration=10" -c:a aac silence_10s.m4a

class MpvProcess:
    def __init__(self, ipc_socket):
        self.ipc_socket = ipc_socket

    def is_running(self):
        """Return True if mpv IPC socket exists and is connectable."""
        if not os.path.exists(self.ipc_socket):
            return False
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect(self.ipc_socket)
            return True
        except (ConnectionRefusedError, FileNotFoundError, socket.timeout):
            return False

    def start(self):
        """Start mpv with IPC if not already running."""
        if self.is_running():
            print(f"mpv {self.ipc_socket} is already running")
            return None

        if os.path.exists(self.ipc_socket):
            os.remove(self.ipc_socket)

        proc = subprocess.Popen([
            "mpv",
            "--idle=yes",
            "--no-video",
            f"--input-ipc-server={self.ipc_socket}",
            "--really-quiet"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return proc

    def wait_for_ipc(self, timeout=2.0):
        """Wait until mpv IPC socket exists and is connectable."""
        start = time.time()
        while True:
            if os.path.exists(self.ipc_socket):
                try:
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        s.connect(self.ipc_socket)
                    return True
                except (ConnectionRefusedError, socket.timeout):
                    pass
            if time.time() - start > timeout:
                return False
            time.sleep(0.05)

    def send_command(self, cmd, args=None):
        if args is None:
            args = []
        message = (json.dumps({"command": [cmd] + args}) + "\n").encode("utf-8")
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                print(f"Sending command to {self.ipc_socket}: {message}")
                s.connect(self.ipc_socket)
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
                print(f"mpv response ({self.ipc_socket}): {decoded}")
        except (ConnectionRefusedError, FileNotFoundError):
            print(f"mpv {self.ipc_socket} is not running or IPC socket missing")

    def play_file_on_loop(self, file_path):
        self.send_command("set_property", ["loop-file", "inf"])
        self.send_command("loadfile", [file_path])

    def play_files_on_loop(self, file_1, file_2):
        self.send_command("playlist_clear")
        self.send_command("set_property", ["loop-playlist", "inf"])
        self.send_command("loadfile", [file_1, "append-play"])
        self.send_command("loadfile", [file_2, "append-play"])

    def set_volume(self, vol):
        self.send_command("set_property", ["volume", vol])


def play_alarms():
    alarm_player = MpvProcess(ALARM_SOCKET)
    announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)

    alarm_player.start()
    announcement_player.start()

    if not alarm_player.wait_for_ipc(timeout=30.0):
        print(f"Error: mpv alarm IPC socket at {ALARM_SOCKET} not ready")
        exit(1)

    if not announcement_player.wait_for_ipc(timeout=30.0):
        print(f"Error: mpv announcement IPC socket at {ANNOUNCEMENT_SOCKET} not ready")
        exit(1)

    alarm_player.set_volume(DEFAULT_VOLUME)
    announcement_player.set_volume(DEFAULT_VOLUME)

    # Play the alarm
    alarm_player.play_file_on_loop(ALARM_FILE)

    # Start the looping announcement playlist
    announcement_player.play_files_on_loop(ANNOUNCEMENT_FILE, SILENCE_FILE)

    print("Done")

# Example usage
if __name__ == "__main__":
    play_alarms()
