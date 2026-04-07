import subprocess
import time
import json
import socket
import os
import logging
import time
from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

"""
Manages the mpv process for playing alarm and announcement sounds. Uses mpv's IPC interface to control playback and volume.

Requires mpv with IPC support (version 0.32.0 or later). On Debian/Ubuntu, the default mpv package does not include IPC. You can install a version with IPC support using:

sudo apt install mpv
"""

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
            logger.debug(f"mpv {self.ipc_socket} is already running")
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
                logger.debug(f"Sending command to {self.ipc_socket}: {message}")
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
                logger.debug(f"mpv response ({self.ipc_socket}): {decoded}")
        except (ConnectionRefusedError, FileNotFoundError):
            logger.debug(f"mpv {self.ipc_socket} is not running or IPC socket missing")

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
            logger.debug("mpv is not running or IPC socket missing")
        return None

    def play_file_on_loop(self, file_path, max_length):
        num_loops = self.num_loops(max_length, file_path)
        self.send_command("set_property", ["loop-file", num_loops])
        self.send_command("loadfile", [file_path])

    def play_files_on_loop(self, file_path_1, file_path_2, max_length):
        num_loops = self.num_loops(max_length, file_path_1, file_path_2)
        self.send_command("playlist_clear")
        self.send_command("set_property", ["loop-playlist", num_loops])
        self.send_command("loadfile", [file_path_1, "append-play"])
        self.send_command("loadfile", [file_path_2, "append-play"])

    def set_volume(self, vol):
        self.send_command("set_property", ["volume", vol])

    def stop(self):
        self.send_command("stop")

    def num_loops(self, max_length, *file_paths):
        total_length = sum(self.track_length(fp) for fp in file_paths)
        return max(1, int(max_length // total_length))

    def track_length(self, file_path):
        audio = MP3(file_path)
        return audio.info.length

# This calculates the steps, but does not do the waiting, so that multiple players can be
# faded out together without needing to use threads. The caller can call step() repeatedly
# with a sleep in between, until it returns True to indicate it's done.
# Could have used threads to do this, but trying to minimise resource usage on the Pi.
# Also, this needs to be called by an HTTP endpoint, so I don't like to add extra
# treads in an HTTP server.
class FadeOut:
    def __init__(self, mpv_process, target_volume, num_steps=10):
        self.mpv_process = mpv_process
        self.target_volume = target_volume
        self.num_steps = num_steps
        self.initial_volume = int(volume) if (volume := mpv_process.get_property("volume")) is not None else None
        # convert this to an array of volume levels to step through, from initial_volume down to target_volume
        self.percentages = list(reversed(range(0, 100, 100 // num_steps)))
        self.current_step = 0

    def step(self):
        if self.current_step < len(self.percentages):
            percent = self.percentages[self.current_step]
            new_volume = self.initial_volume * percent // 100
            self.mpv_process.set_volume(new_volume)
            self.current_step += 1
            return False  # not done yet
        else:
            self.mpv_process.stop()
            logger.info("Stopped mpv player with IPC socket: %s", self.mpv_process.ipc_socket)
            return True  # done

"""
Gradually fade out the volume of the given mpv processes over the specified duration and steps, then stop them.
"""
def fade_out(mvp_processes, duration=2.0, steps=10):

    fade_outs = []
    for player in mvp_processes:
        fade_outs.append(FadeOut(player, target_volume=0, num_steps=steps))

    step_time = duration / steps

    while fade_outs:
        for fade in fade_outs[:]:
            if fade.step():
                fade_outs.remove(fade)
        time.sleep(step_time) if fade_outs else None
