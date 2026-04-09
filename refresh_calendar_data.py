from ecal.env import DATA_DIRECTORY
from google_calendar import CalendarSource
import json
from datetime import datetime, date
import dataclasses
from ecal.env import filter

"""
This script refreshes the calendar data and saves it to a local file. It is for dev and test only.
"""

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

def json_default_encoder(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    return str(o)

if __name__ == "__main__":
    calendar_source = CalendarSource(stubbed=False)
    creds = calendar_source.load_creds()
    calendars = calendar_source.load_data(creds, filter)
    data_json = json.dumps(calendars, sort_keys=True, default=json_default_encoder)

    with open(DATA_FILE, "w") as f:
            f.write(data_json)
