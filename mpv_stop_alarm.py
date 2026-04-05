import subprocess
import time
import json
import socket
import os

IPC_SOCKET = "/tmp/mpv_socket"

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

if __name__ == "__main__":
    fade_out(3)
