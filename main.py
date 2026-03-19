from google_calendar import CalendarSource
from pathlib import Path
from layout import layout_calendars
from model import Surface
from qr import make_qr_code
from datetime import datetime, date
import json
import dataclasses
from env import filter, SERVER_ADDRESS, DATA_DIRECTORY, IS_LOCAL
import sys

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

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
        epd = epd12in48b.EPD()
        epd.Init()
        Redimage = Image.new("1", (epd12in48b.EPD_WIDTH, epd12in48b.EPD_HEIGHT), 255)
        epd.display(image, Redimage)
        epd.EPD_Sleep()

    except IOError as e:
        print(f"error: {e}")

    except KeyboardInterrupt:
        print("ctrl + c:")
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
            print("last_render == '["credentials"]' whatever that means")
            return
        print("unable to load creds, rendering qr code for re-auth")
        return make_qr_code(SERVER_ADDRESS, surface)
    else:
        print("loading calendars")
        calendars = calendar_source.load_data(creds, filter)
        data_json = json.dumps(calendars, sort_keys=True, default=json_default_encoder)
        if last_render == data_json and not force:
            print("Calendar data has not changed, and force is not true, so returning None")
            return
        with open(DATA_FILE, "w") as f:
            f.write(data_json)
        return layout_calendars(calendars, surface)


def run(render, load_creds, width, height, force):
    surface = Surface(0, 0, width, height)
    image = load_image(load_creds, surface, force)
    if image is None:
        print("no update")
    else:
        print("updating")
        render(image)


if __name__ == "__main__":
    force = (len(sys.argv) > 1 and sys.argv[1] == "--force")
    print("running: " + datetime.now().isoformat() + " force=" + str(force), flush=True)
    if IS_LOCAL:
        print("Rendering locally")
        run(local_render, CalendarSource(stubbed=True), 1304, 984, force)
    else:
        print("Refreshing hardware screen")
        run(hardware_render, CalendarSource(stubbed=False), 1304, 984, force)
    print("finished")

