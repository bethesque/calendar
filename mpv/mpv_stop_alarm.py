import time
import logging
from mpv import MpvProcess

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

def fade_out(mvp_processes, duration=2.0, steps=10):
    """
    Gradually fade out the volume of the given mpv processes over the specified duration and steps, then stop them.
    """
    
    processes_to_fade = []
    for player in mvp_processes:
        volume = int(volume) if (volume := player.get_property("volume")) is not None else None
        if volume is not None:
            processes_to_fade.append((player, volume))

    step_time = duration / steps

    for percent_vol in reversed(range(0, 100, 100 // steps)):
        for player, volume in processes_to_fade:
            player.set_volume(volume * percent_vol // 100)
        time.sleep(step_time)
    
    for player in mvp_processes:
        player.stop()

if __name__ == "__main__":
    alarm_player = MpvProcess(ALARM_SOCKET)
    announcement_player = MpvProcess(ANNOUNCEMENT_SOCKET)
    fade_out([alarm_player, announcement_player], 3)
