import time
from mpv import MpvProcess

ALARM_SOCKET = "/tmp/mpv_alarm.sock"
ANNOUNCEMENT_SOCKET = "/tmp/mpv_announcement.sock"

def fade_out(duration=2.0, steps=10):
    alarm_player = mpv.MpvProcess(ALARM_SOCKET)
    announcement_player = mpv.MpvProcess(ANNOUNCEMENT_SOCKET)

    # Get current volume from alarm socket
    initial_alarm_volume = int(volume) if (volume := alarm_player.get_property("volume")) is not None else None

    # Get current volume from announcement socket
    initial_announcement_volume = int(volume) if (volume := announcement_player.get_property("volume")) is not None else None

    step_time = duration / steps

    for vol in reversed(range(0, 100, 100 // steps)):
        if initial_alarm_volume is not None and initial_alarm_volume > 0:
            alarm_player.set_volume(initial_alarm_volume * vol // 100)

        if initial_announcement_volume is not None and initial_announcement_volume > 0:
            announcement_player.set_volume(initial_announcement_volume * vol // 100)
        
        time.sleep(step_time)
    
    alarm_player.stop()
    announcement_player.stop()

if __name__ == "__main__":
    fade_out(3)
