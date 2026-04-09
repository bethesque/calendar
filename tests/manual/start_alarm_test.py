import sys
import os

from ecal.alarms import ALARM_SOCKET, ANNOUNCEMENT_SOCKET
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))

from ecal.alarms.alarm import play_alarm
from ecal.alarms.mpv import MpvProcess, fade_out
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )

# Example usage
if __name__ == "__main__":
    try:
        play_alarm(["audio/test_announcement.mp3"])
    except KeyboardInterrupt as e:
        alarm_player = MpvProcess(ALARM_SOCKET)
        announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
        fade_out([alarm_player, announcement_player], 3)
        exit(0)
