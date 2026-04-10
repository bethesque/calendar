import sys
import logging
from ecal.log_config import setup_logging_for_cron
from ecal.google_calendar import CalendarSource
from datetime import datetime
from ecal.env import IS_LOCAL, STUB_DATA
from ecal.screen.image import local_render
from ecal.screen.hardware_screen import hardware_render
from ecal.screen.model import Surface
from ecal.screen.image import load_image

setup_logging_for_cron()

logger = logging.getLogger(__name__)

def run(render, calendar_source, force):
    surface = Surface(*Surface.DEFAULT_DIMENSIONS)
    image = load_image(calendar_source, surface, force)
    if image is None:
        logger.info("no update")
    else:
        logger.info("updating")
        render(image)

if __name__ == "__main__":
    force = (len(sys.argv) > 1 and sys.argv[1] == "--force")
    logger.info("running: " + datetime.now().isoformat() + " force=" + str(force) + " IS_LOCAL=" + str(IS_LOCAL) + " STUB_DATA=" + str(STUB_DATA))

    calendar_source = CalendarSource(stubbed=STUB_DATA)
    renderer = local_render if IS_LOCAL else hardware_render

    run(renderer, calendar_source, force)
    logger.info("finished")
