from mpv import MpvProcess
from config import ALARM_FILE, ALARM_SOCKET, ANNOUNCEMENT_FILE, ANNOUNCEMENT_SOCKET, SILENCE_FILE, DEFAULT_VOLUME
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )


# Note: You'll need to create a 10-second silent audio file named "silence_10s.m4a"
# You can create one with: ffmpeg -f lavfi -i "sine=frequency=0:duration=10" -c:a aac silence_10s.m4a

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
