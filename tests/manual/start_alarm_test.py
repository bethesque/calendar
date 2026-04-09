import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))

from ecal.alarms.alarm import play_alarm
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
    play_alarm(["audio/test_announcement.mp3"])
