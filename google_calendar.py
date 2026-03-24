from __future__ import print_function

import datetime
from zoneinfo import ZoneInfo
import os.path
from dataclasses import dataclass, field
from operator import attrgetter
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TIMEZONE = "Australia/Melbourne"

logger = logging.getLogger(__name__)


@dataclass
class GoogleCalendar:
    id: str
    name: str


@dataclass
class Event:
    owner: str
    summary: str
    description: str
    start_time: datetime.time = None
    end_time: datetime.time = None
    recurring: bool = False


# A day displayed on the calendar screen
@dataclass
class CalendarDay:
    date: datetime.date
    whole_day_events: list[Event] = field(default_factory=list)
    timed_events: list[Event] = field(default_factory=list)
    date_time: datetime.datetime = None

    def __post_init__(self):
        self.date_time = datetime.datetime.combine(self.date, datetime.time.min, tzinfo=ZoneInfo(TIMEZONE))


def load_google_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_filename = "token.json"
    if os.path.exists(token_filename):
        creds = Credentials.from_authorized_user_file(token_filename, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            creds = None

    return creds


def list_google_calendars(creds):
    try:
        service = build("calendar", "v3", credentials=creds)
        result = service.calendarList().list().execute()
        return [GoogleCalendar(c["id"], c["summary"]) for c in result.get("items", [])]
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return []


def list_google_events(creds, calendar_id, min, max):
    try:
        service = build("calendar", "v3", credentials=creds)
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=min.isoformat(),
                timeMax=max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    except HttpError as error:
        logger.info("An error occurred: %s" % error)
        return []


def add_events_to_calendars(events_from_google, calendar_name, displayed_calendar_days):
    for event_dict in events_from_google:
        
        matched_days = [d for d in displayed_calendar_days if displayed_day_includes_event(d, event_dict)]

        for matched_day in matched_days:
            event = Event(owner=calendar_name, summary=event_dict["summary"], description=event_dict.get("description"), recurring=bool(event_dict.get("recurringEventId")))
            if "dateTime" in event_dict["start"]: # has a time specified
                event.start_time = datetime.datetime.fromisoformat(event_dict["start"]["dateTime"])
                matched_day.timed_events.append(event)
            else:
                matched_day.whole_day_events.append(event)

"""
Returns true if the event described by the properties in the event_dict falls on the date
of the given displayed CalendarDay.

Properties:

event_dict: dict
    The Google Calendar event dict.
"""
def displayed_day_includes_event(displayed_calendar_day, event_dict):
    start = event_dict["start"] # dict with either "date" or "dateTime" as a string
    start_date_text = start.get("date", start.get("dateTime"))
    start_date = datetime.datetime.fromisoformat(start_date_text).date()

    end = event_dict["end"] # dict with either "date" or "dateTime" as a string
    end_date_text = end.get("date", end.get("dateTime"))
    end_date_time = datetime.datetime.fromisoformat(end_date_text)

    if end_date_time.tzinfo is None:
        end_date_time = end_date_time.replace(tzinfo=ZoneInfo(TIMEZONE))

    return displayed_calendar_day.date == start_date or ( start_date < displayed_calendar_day.date and displayed_calendar_day.date_time < end_date_time )     


def get_calendars(creds, filter):
    google_calendars = list_google_calendars(creds)
    google_calendars_by_id = {calendar.id: calendar for calendar in google_calendars}
    start_of_today = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min, tzinfo=ZoneInfo(TIMEZONE)
    )
    tomorrow = start_of_today + datetime.timedelta(days=1)
    end_of_tomorrow = tomorrow + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
    displayed_calendar_days = [CalendarDay(date=start_of_today.date()), CalendarDay(date=tomorrow.date())]
    
    for cal_id, display_name in filter:
        gcal = google_calendars_by_id[cal_id]
        if gcal:
            events = list_google_events(
                creds,
                gcal.id,
                start_of_today,
                end_of_tomorrow,
            )
            logger.info(f"Adding events from id: {gcal.id} name: {gcal.name}")
            add_events_to_calendars(events, display_name, displayed_calendar_days)

    for cal in displayed_calendar_days:
        cal.timed_events.sort(key=attrgetter("start_time"))
    return displayed_calendar_days


def test_data():
    today = datetime.datetime.combine(
        datetime.date.today(), datetime.time.min, tzinfo=ZoneInfo(TIMEZONE)
    )
    tomorrow = today + datetime.timedelta(days=1)
    calendars = [CalendarDay(date=today.date()), CalendarDay(date=tomorrow.date())]
    today = calendars[0]
    tomorrow = calendars[1]
    today.whole_day_events.append(Event("Trav", "Working on calendar epaper thing", "Once off event"))
    today.whole_day_events.append(Event("Trav", "A very important event", "#veryimportant", recurring=True))
    today.whole_day_events.append(Event("Trav", "A normal recurring event", "", recurring=True))
    today.whole_day_events.append(Event("Trav", "An important recurring event", "#important", recurring=True))
    today.whole_day_events.append(Event("Beth", "A once off unimportant event", "#notimportant", recurring=True))
    today.timed_events.append(
        Event(
            "Beth",
            "A very long summary that is going to take way more space than we have to fit in the calendar horizontally which will cause it to split across multiple lines",
            None,
            datetime.datetime(2023, 11, 2, 11, 30, tzinfo=ZoneInfo(TIMEZONE)),
        )
    )
    event_time = datetime.datetime(2023, 11, 3, 9, tzinfo=ZoneInfo(TIMEZONE))
    for n in range(10):
        tomorrow.timed_events.append(Event("B & T", f"fake event #{n}", None, event_time, recurring=True))
        event_time = event_time + datetime.timedelta(minutes=30)
    return calendars


@dataclass
class FakeCreds:
    valid: bool


@dataclass
class CalendarSource:
    stubbed: bool

    def load_creds(self):
        if self.stubbed:
            return FakeCreds(valid=True)
        return load_google_creds()

    def load_data(self, creds, filter):
        if self.stubbed:
            return test_data()
        return get_calendars(creds, filter)


if __name__ == "__main__":
    print(f"calendars: {get_calendars()}")
