import subprocess
import time
import json
import socket
import os
import logging

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
            logging.debug(f"mpv {self.ipc_socket} is already running")
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
                logging.debug(f"Sending command to {self.ipc_socket}: {message}")
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
                logging.debug(f"mpv response ({self.ipc_socket}): {decoded}")
        except (ConnectionRefusedError, FileNotFoundError):
            logging.debug(f"mpv {self.ipc_socket} is not running or IPC socket missing")

    def get_property(self, property_name):
        """Get a property value from mpv."""
        message = json.dumps({"command": ["get_property", property_name]}) + "\n"
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(self.ipc_socket)
                s.sendall(message.encode("utf-8"))
                # Read response
                response = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                    if b"\n" in response:
                        break
                try:
                    data = json.loads(response.decode("utf-8").strip())
                    if "data" in data:
                        return data["data"]
                except json.JSONDecodeError:
                    pass
        except (ConnectionRefusedError, FileNotFoundError):
            logging.debug("mpv is not running or IPC socket missing")
        return None            

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

    def stop(self):
        self.send_command("stop")    
