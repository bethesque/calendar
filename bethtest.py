import logging
import time
from mpv.mpv import MpvProcess, fade_up
from mpv.config import ALARM_FILE, ALARM_SOCKET, ANNOUNCEMENT_SOCKET, SILENCE_FILE, DEFAULT_VOLUME

logger = logging.getLogger(__name__)

def play_alarm(announcement_file):
    alarm_player = MpvProcess(ALARM_SOCKET)
    announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)

    alarm_player.start()
    announcement_player.start()

    if not alarm_player.wait_for_ipc(timeout=30.0):
        logger.error(f"Error: mpv alarm IPC socket at {ALARM_SOCKET} not ready")
        exit(1)

    if not announcement_player.wait_for_ipc(timeout=30.0):
        logger.error(f"Error: mpv announcement IPC socket at {ANNOUNCEMENT_SOCKET} not ready")
        exit(1)

    alarm_player.set_volume(DEFAULT_VOLUME)
    announcement_player.set_volume(DEFAULT_VOLUME)

    # Play the alarm
    alarm_player.play_file_on_loop(ALARM_FILE, 240)

    # Start the looping announcement playlist
    announcement_player.play_files_on_loop(SILENCE_FILE, announcement_file, 240)

    fade_up([(alarm_player, 80), (announcement_player, 80)], 45, 10)

    logger.info("Done")