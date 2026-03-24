from google_calendar import CalendarSource
from pathlib import Path
from layout import layout_calendars
from model import Surface
from qr import make_qr_code
from datetime import datetime, date
import json
import dataclasses
from env import filter, SERVER_ADDRESS, DATA_DIRECTORY, IS_LOCAL, STUB_DATA
from log_config import setup_logging
import logging
import sys
import time

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

setup_logging()

logger = logging.getLogger(__name__)

def json_default_encoder(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    return str(o)


def hardware_render(image):
    from waveshare_epd import epd12in48b
    from PIL import Image

    try:
        start = time.perf_counter()
        epd = epd12in48b.EPD()
        epd.Init()
        RedImage = Image.new("1", (epd12in48b.EPD_WIDTH, epd12in48b.EPD_HEIGHT), 255)
        epd.display(image, RedImage)
        epd.EPD_Sleep()
        end = time.perf_counter()
        logger.info("hardware_render time: %.3f seconds", end - start)
    except IOError as e:
        logger.error(f"error: {e}")

    except KeyboardInterrupt:
        logger.info("ctrl + c:")
        epd12in48b.epdconfig.module_exit()
        exit()


def local_render(image):
    image.show("test")


def load_image(calendar_source, surface, force):
    last_render = None
    try:
        with open(DATA_FILE) as f:
            last_render = f.read()
    except:
        pass
    creds = calendar_source.load_creds()
    if not creds or not creds.valid:
        with open(DATA_FILE, "w") as f:
            f.write('["credentials"]')
        if last_render == '["credentials"]':
            logger.info("last_render == '[credentials]' whatever that means")
            return
        logger.info("unable to load creds, rendering qr code for re-auth")
        return make_qr_code(SERVER_ADDRESS, surface)
    else:
        logger.info("loading calendars")
        calendars = calendar_source.load_data(creds, filter)
        data_json = json.dumps(calendars, sort_keys=True, default=json_default_encoder)
        if last_render == data_json and not force:
            logger.info("Calendar data has not changed, and force is not true, so returning None")
            return
        with open(DATA_FILE, "w") as f:
            f.write(data_json)
        return layout_calendars(calendars, surface)


def run(render, load_creds, width, height, force):
    surface = Surface(0, 0, width, height)
    image = load_image(load_creds, surface, force)
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

    run(renderer, calendar_source, 1304, 984, force)
    logger.info("finished")
