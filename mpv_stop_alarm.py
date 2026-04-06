import time
import json
import socket

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"

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

def stop_alarm(ipc_socket):
    send_command(ipc_socket, "stop")

def set_volume(ipc_socket, vol):
    send_command(ipc_socket, "set_property", ["volume", vol])

def fade_out(duration=2.0, steps=10):
    step_time = duration / steps
    for vol in reversed(range(0, 101, 100 // steps)):
        set_volume(ALARM_SOCKET, vol)
        set_volume(ANNOUNCEMENT_SOCKET, vol)
        time.sleep(step_time)
    stop_alarm(ALARM_SOCKET)
    stop_alarm(ANNOUNCEMENT_SOCKET)

if __name__ == "__main__":
    fade_out(3)
