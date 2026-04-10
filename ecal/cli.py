from ecal.env import DATA_DIRECTORY
from ecal.google_calendar import CalendarSource
import json
from ecal.env import filter
from ecal.string_utils import json_default_encoder

"""
This script refreshes the calendar data and saves it to a local file. It is for dev and test only.
"""

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

def refresh_calendar_data():
    print(f"Refreshing calendar data in {DATA_FILE}...")
    calendar_source = CalendarSource(stubbed=False)
    creds = calendar_source.load_creds()
    calendars = calendar_source.fetch_data(creds, filter)
    data_json = json.dumps(calendars, sort_keys=True, default=json_default_encoder)

    with open(DATA_FILE, "w") as f:
            f.write(data_json)
