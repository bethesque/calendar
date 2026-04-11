from ecal.env import DATA_DIRECTORY
from ecal.google_calendar import CalendarSource
from ecal.env import filter

"""
This script refreshes the calendar data and saves it to a local file. It is for dev and test only.
"""

DATA_FILE = DATA_DIRECTORY + "/ecalendar-last-render.json"

def refresh_calendar_data():
    print(f"Refreshing calendar data in {DATA_FILE}...")
    calendar_source = CalendarSource(stubbed=False)
    creds = calendar_source.load_creds()
    calendar_days = calendar_source.fetch_data(creds, filter)
    calendar_source.save_data_to_file(DATA_FILE, calendar_days)
