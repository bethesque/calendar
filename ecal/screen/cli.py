import logging
import platform
from ecal.env import DATA_DIRECTORY, IS_LOCAL
from ecal.google_calendar import CalendarSource
from ecal.screen.image import load_image, local_render
from ecal.screen.hardware_screen import hardware_render
from ecal.screen.model import Surface
from ecal.log_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

"""
Load the existing calendar data from the local file and render it.
This is for dev and test only, to make it easier to iterate on the
screen layout without having to fetch data from the Google Calendar API every time.
"""
def render():
    calendar_source = CalendarSource(stubbed=False)
    surface = Surface(*Surface.DEFAULT_DIMENSIONS)
    image = load_image(calendar_source, surface, True, True)
    logger.info("Rendering calendar image")
    renderer = local_render if IS_LOCAL else hardware_render
    renderer(image)

def clear_screen():
        # if is mac
    if platform.system() == "Darwin":
        logging.info("Running on macOS, skipping hardware rendering")
        exit()

    from waveshare_epd import epd12in48b

    try:
        epd = epd12in48b.EPD()
        logging.info("init")
        epd.init()
        logging.info("Clear")
        epd.Clear()
        logging.info("sleep")
        epd.sleep()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd12in48b.epdconfig.module_exit()
        exit()
