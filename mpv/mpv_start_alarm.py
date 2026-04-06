from mpv import mpv

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"

ALARM_FILE = "audio/alarm.mp3"
ANNOUNCEMENT_FILE = "audio/announcement.mp3"
SILENCE_FILE = "audio/silence_5s.m4a"

DEFAULT_VOLUME = 50

# Note: You'll need to create a 10-second silent audio file named "silence_10s.m4a"
# You can create one with: ffmpeg -f lavfi -i "sine=frequency=0:duration=10" -c:a aac silence_10s.m4a

def play_alarms():
    alarm_player = mpv.MpvProcess(ALARM_SOCKET)
    announcement_player = mpv.MpvProcess(ANNOUNCEMENT_SOCKET)

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
