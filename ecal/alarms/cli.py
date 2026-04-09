import logging

from ecal.alarms.alarm import play_alarm
from ecal.alarms import ALARM_SOCKET, ANNOUNCEMENT_SOCKET
from ecal.alarms.mpv import MpvProcess, fade_out
from ecal.log_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

def test_alarm():
    try:
        play_alarm(["audio/test_announcement.mp3"])
    except KeyboardInterrupt as e:
        alarm_player = MpvProcess(ALARM_SOCKET)
        announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
        fade_out([alarm_player, announcement_player], 3)
        exit(0)

def stop_alarm():
    try:
        alarm_player = MpvProcess(ALARM_SOCKET)
        announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
        fade_out([alarm_player, announcement_player], 3)
        logger.info("Alarm stopped.")
    except Exception as e:
        logger.error(f"Error stopping alarm: {e}")
        exit(1)
