from ecal.screen.layout import layout_calendars
from ecal.screen.model import Surface
from ecal.screen.hardware_screen import hardware_render
from ecal.screen.qr import make_qr_code
import json
from datetime import datetime
from ecal.string_utils import json_default_encoder
from ecal.env import filter, SERVER_ADDRESS, DATA_DIRECTORY, IS_LOCAL, STUB_DATA
from ecal.log_config import setup_logging
import logging
import sys

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

logger = logging.getLogger(__name__)

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
        calendars = calendar_source.fetch_data(creds, filter)
        data_json = json.dumps(calendars, sort_keys=True, default=json_default_encoder)
        if last_render == data_json and not force:
            logger.info("Calendar data has not changed, and force is not true, so returning None")
            return
        with open(DATA_FILE, "w") as f:
            f.write(data_json)
        return layout_calendars(calendars, surface)

def local_render(image):
    image.show("test")
