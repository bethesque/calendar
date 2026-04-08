from bethtest import play_alarm
from mpv.config import ANNOUNCEMENT_FILE
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Note: You'll need to create a 10-second silent audio file named "silence_10s.m4a"
# You can create one with: ffmpeg -f lavfi -i "sine=frequency=0:duration=10" -c:a aac silence_10s.m4a


# Example usage
if __name__ == "__main__":
    play_alarm(["audio/test_announcement.mp3"])
