from ecal.screen.rendering import *
from ecal.google_calendar import CalendarDay, WeatherForecast
import datetime

weekdays = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
LEFT_WIDTH = 90

def layout_calendars(calendar_days: list[CalendarDay], surface):
    image = Image.new(
        "RGB", (surface.right, surface.bottom), surface.BLACK
    )  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    calendar_day_scrollers = [ CalendarDayEventScroller(day) for day in calendar_days]

    events_fit = False
    more_events_can_be_hidden = True
    # Do a dry run render. If there are any events that do not fit, keep
    # removing past events for the current day until either the events fit,
    # or there are no more past events that can be hidden.
    while not events_fit and more_events_can_be_hidden:
        try:
            box = layout_calendar_days(calendar_day_scrollers)
            box.render(draw, image, surface, True)
            events_fit = True
        except ChildrenDoNotFit:
            more_events_can_be_hidden = calendar_day_scrollers[0].pop_past_timed_event()

    # Do the real render
    box.render(draw, image, surface)

    return image

def layout_calendar_days(calendar_day_scrollers):
    box = EqualChildrenBox(padding=5, stroke=0)
    h1_font = font(size=FONT_SIZE_H1)

    for day in calendar_day_scrollers:
        day_box = StackChildrenBox(padding=5, stroke=0, horizontal=False)
        day_box.children.append(
            Text(
                f"{weekdays[day.date.weekday()]} {day.date.strftime('%d/%m/%Y')}",
                font=h1_font,
                color=WHITE,
            ),
        )

        for event in day.whole_day_events:
            summary = extract_summary(event)
            summary_font = decide_summary_font(event)

            left_thing = Text(event.owner)
            if isinstance(event, WeatherForecast):
                left_thing = Icon(file_path=event.image_path)

            day_box.children.append(
                RightStretchBox(
                    fill=WHITE,
                    margin=2,
                    left_width=LEFT_WIDTH,
                    left=left_thing,
                    right=Text(summary, font=summary_font, color=BLACK),
                )
            )
        for event in day.timed_events:
            summary = extract_summary(event)
            summary_font = decide_summary_font(event)

            day_box.children.append(
                RightStretchBox(
                    fill=WHITE,
                    margin=2,
                    left_width=LEFT_WIDTH,
                    left=Text(
                        f"{event.owner}\n{event.start_time.strftime('%I:%M %p')}"
                    ),
                    right=Text(summary, font=summary_font, padding_top=4, color=BLACK),
                )
            )

        box.children.append(day_box)

    return box


def extract_summary(event):
    return "*** " + event.summary.upper() + " ***" if event.description and "#veryimportant" in event.description else event.summary

def decide_summary_font(event):
    return important_font(size=FONT_SIZE_SUMMARY - 1) if is_important(event) else font(size=FONT_SIZE_SUMMARY)


def is_important(event):
    marked_important = event.description and "#important" in event.description
    marked_very_important = event.description and "#veryimportant" in event.description
    marked_not_important = event.description and "#notimportant" in event.description
    once_off_event = not event.recurring
    return marked_important or marked_very_important or (once_off_event and not marked_not_important)

"""
A proxy class for CalendarDay which supports hiding past events when the timed
events do not all fit on the screen.
"""
class CalendarDayEventScroller:
    def __init__(self, calender_day: CalendarDay):
        self._calendar_day = calender_day
        self._timed_events_start_index = 0
        self.timed_events = list(calender_day.timed_events)

    def __getattr__(self, name):
        # Redirect all calls to the target object
        return getattr(self._calendar_day, name)

    # When it's not possible to fit all the timed events onto the screen,
    # allow a past event to be hidden.
    # Returns True if there are any more past events that can be hidden.
    def pop_past_timed_event(self, date_time=datetime.datetime.now().astimezone()):
        index = self._index_of_next_event_ending_in_past(date_time)
        if index != -1:
            self.timed_events.pop(index)

        return self.any_events_in_past(date_time)

    def any_events_in_past(self, date_time):
        return self._index_of_next_event_ending_in_past(date_time) != -1

    def _index_of_next_event_ending_in_past(self, date_time) -> int:
        for i, event in enumerate(self.timed_events):
            if event.past_end(date_time):
                return i
        return -1

