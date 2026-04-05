import json
import logging
import sys, os
import argparse
import subprocess
from datetime import datetime, timedelta
from log_config import setup_logging
from env import ALARM_PID_FILE, DATA_DIRECTORY

setup_logging()

logger = logging.getLogger(__name__)

def load_events(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def parse_iso(dt_str):
    return datetime.fromisoformat(dt_str)

def get_time_window(base_time, window_minutes):
    # Round down to nearest multiple of WINDOW
    minute = (base_time.minute // window_minutes) * window_minutes
    start_time = base_time.replace(minute=minute, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=window_minutes)
    return start_time, end_time

def find_events_in_range(events_data, start_time, end_time):
    matching_events = []

    for day in events_data:
        for event in day.get("timed_events", []):
            start_str = event.get("start_time")
            if not start_str:
                continue

            event_start = parse_iso(start_str)

            if start_time <= event_start < end_time:
                matching_events.append(event)

    return matching_events

def alarm_player():
    if sys.platform == "darwin":
        return "afplay"
    elif sys.platform.startswith("linux"):
        return "mpg123"
    else:
        raise NotImplementedError("Unsupported platform")

def play_alarm():
    logging.info("Playing alarm sound")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, "log.txt")
    alarm_file = os.path.join(script_dir, "alarm.mp3")
    with open(log_file, "a") as f:
        process = subprocess.Popen([alarm_player(), alarm_file], stdout=f, stderr=subprocess.STDOUT)
    with open(ALARM_PID_FILE, "w") as f:
        f.write(str(process.pid))
    logging.info("Alarm process started with PID: %d", process.pid)

def log_results(results):
    for result in results:
        logging.info(
            "Matched event: %s | %s",
            result.get("start_time"),
            result.get("summary")
        )
    logging.info("Total matched events: %d", len(results))

def check_for_alarms(base_time, window, calendar_data):
    start, end = get_time_window(base_time, window)

    logging.info(
        "Time window: %s → %s (WINDOW=%d mins)",
        start.isoformat(),
        end.isoformat(),
        window
    )
    results = find_events_in_range(calendar_data, start, end)
    log_results(results)

    if results:
        play_alarm()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for alarms in calendar events")
    parser.add_argument(
        "--base_time",
        type=lambda s: datetime.fromisoformat(s),
        default=None,
        help="Base time for checking alarms (ISO format, defaults to current time)"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=5,
        help="Time window in minutes for checking alarms (default: 5)"
    )

    args = parser.parse_args()
    base_time = args.base_time or datetime.now().astimezone()
    calendar_data_file_path = DATA_DIRECTORY + "/ecalendar-last-render.json"
    calendar_data = load_events(calendar_data_file_path)
    
    check_for_alarms(base_time, args.window, calendar_data)
