import time
import logging
from mpv import MpvProcess, fade_out


logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"

if __name__ == "__main__":
    alarm_player = MpvProcess(ALARM_SOCKET)
    announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
    fade_out([alarm_player, announcement_player], 3)
