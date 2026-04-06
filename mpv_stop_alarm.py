import logging
from mpv.config import ALARM_SOCKET, ANNOUNCEMENT_SOCKET
from mpv.mpv import MpvProcess, fade_out


logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    alarm_player = MpvProcess(ALARM_SOCKET)
    announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
    fade_out([alarm_player, announcement_player], 3)
