import pytest
import datetime
from zoneinfo import ZoneInfo

from ecal.screen.layout import CalendarDayEventScroller
from ecal.google_calendar import CalendarDay, Event


@pytest.fixture
def timezone():
    """Provide the test timezone."""
    return ZoneInfo("Australia/Melbourne")


@pytest.fixture
def current_time(timezone):
    """Provide a fixed reference time for testing."""
    return datetime.datetime(2026, 5, 6, 14, 30, 0, tzinfo=timezone)


@pytest.fixture
def test_date():
    """Provide a test date."""
    return datetime.date(2026, 5, 6)


def create_event(summary, start_time, end_time=None, owner="Test Owner", recurring=False):
    """Helper to create an Event with a specific start and end time."""
    if end_time is None:
        end_time = start_time + datetime.timedelta(hours=1)
    return Event(
        owner=owner,
        summary=summary,
        description="",
        start_time=start_time,
        end_time=end_time,
        recurring=recurring
    )


class TestPopPastTimedEvent:
    """Tests for pop_past_timed_event method."""

    def test_no_events(self, test_date, current_time):
        """Test pop_past_timed_event when there are no timed events."""
        calendar_day = CalendarDay(date=test_date, timed_events=[])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result
        assert len(scroller.timed_events) == 0

    def test_event_end_time_in_past(self, test_date, current_time):
        """Test pop_past_timed_event when event end_time is in the past."""
        start_time = current_time - datetime.timedelta(hours=2)
        end_time = current_time - datetime.timedelta(hours=1)
        event = create_event("Completed Event", start_time, end_time)

        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result
        assert len(scroller.timed_events) == 0

    def test_event_end_time_in_future(self, test_date, current_time):
        """Test pop_past_timed_event when event end_time is in the future."""
        start_time = current_time + datetime.timedelta(hours=1)
        end_time = current_time + datetime.timedelta(hours=2)
        event = create_event("Upcoming Event", start_time, end_time)

        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Upcoming Event"

    def test_multiple_completed_events(self, test_date, current_time):
        """Test pop_past_timed_event with multiple events with end_time in the past."""
        event_1_start = current_time - datetime.timedelta(hours=4)
        event_1_end = current_time - datetime.timedelta(hours=3)
        event_1 = create_event("Completed Event 1", event_1_start, event_1_end)

        event_2_start = current_time - datetime.timedelta(hours=2)
        event_2_end = current_time - datetime.timedelta(hours=1)
        event_2 = create_event("Completed Event 2", event_2_start, event_2_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event_1, event_2])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert result  # Second event also has end_time in the past
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Completed Event 2"

        result = scroller.pop_past_timed_event(current_time)
        assert not result  # No more events with end_time in past
        assert len(scroller.timed_events) == 0

    def test_completed_followed_by_upcoming(self, test_date, current_time):
        """Test pop_past_timed_event with a completed event followed by an upcoming event."""
        completed_start = current_time - datetime.timedelta(hours=2)
        completed_end = current_time - datetime.timedelta(hours=1)
        event_completed = create_event("Completed Event", completed_start, completed_end)

        upcoming_start = current_time + datetime.timedelta(hours=1)
        upcoming_end = current_time + datetime.timedelta(hours=2)
        event_upcoming = create_event("Upcoming Event", upcoming_start, upcoming_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event_completed, event_upcoming])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result  # Next event has end_time in the future
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Upcoming Event"

    def test_does_not_modify_if_end_time_in_future(self, test_date, current_time):
        """Test pop_past_timed_event does not remove events with end_time in the future."""
        event_1_start = current_time + datetime.timedelta(hours=1)
        event_1_end = current_time + datetime.timedelta(hours=2)
        event_1 = create_event("Upcoming Event 1", event_1_start, event_1_end)

        event_2_start = current_time + datetime.timedelta(hours=3)
        event_2_end = current_time + datetime.timedelta(hours=4)
        event_2 = create_event("Upcoming Event 2", event_2_start, event_2_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event_1, event_2])
        scroller = CalendarDayEventScroller(calendar_day)
        initial_length = len(scroller.timed_events)

        result = scroller.pop_past_timed_event(current_time)
        assert not result
        assert len(scroller.timed_events) == initial_length

    def test_with_default_current_time(self, test_date, timezone):
        """Test pop_past_timed_event using default current_time parameter."""
        event_start = datetime.datetime(2000, 1, 1, tzinfo=timezone)
        event_end = datetime.datetime(2000, 1, 2, tzinfo=timezone)
        event = create_event("Ancient Event", event_start, event_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        # Event ended in year 2000, should be popped
        result = scroller.pop_past_timed_event()
        assert not result
        assert len(scroller.timed_events) == 0

    def test_boundary_condition_end_time_equals_current(self, test_date, current_time):
        """Test pop_past_timed_event when event end_time equals current_time."""
        start_time = current_time - datetime.timedelta(hours=1)
        end_time = current_time  # End time equals current time, not in the past
        event = create_event("Boundary Event", start_time, end_time)

        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result  # Not in past (equal means not <)
        assert len(scroller.timed_events) == 1

    def test_ongoing_event_not_popped(self, test_date, current_time):
        """Test pop_past_timed_event does not remove ongoing events (started but not ended)."""
        start_time = current_time - datetime.timedelta(hours=1)
        end_time = current_time + datetime.timedelta(hours=1)
        event = create_event("Ongoing Event", start_time, end_time)

        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result  # Event still has time left (end_time in future)
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Ongoing Event"

    def test_respects_provided_datetime(self, test_date, timezone):
        """Test that pop_past_timed_event correctly uses the provided datetime parameter."""
        reference_time = datetime.datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone)

        # Event 1: ends before reference_time (should be popped)
        event_1_start = reference_time - datetime.timedelta(hours=2)
        event_1_end = reference_time - datetime.timedelta(hours=1)
        event_1 = create_event("Completed Event", event_1_start, event_1_end)

        # Event 2: ends after reference_time (should not be popped)
        event_2_start = reference_time + datetime.timedelta(hours=1)
        event_2_end = reference_time + datetime.timedelta(hours=2)
        event_2 = create_event("Upcoming Event", event_2_start, event_2_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event_1, event_2])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(reference_time)
        assert not result
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Upcoming Event"

    def test_removes_second_event_when_first_is_ongoing(self, test_date, current_time):
        """Test pop_past_timed_event removes the second event when first is ongoing but second is completed."""
        # First event: ongoing (started but not ended)
        ongoing_start = current_time - datetime.timedelta(hours=1)
        ongoing_end = current_time + datetime.timedelta(hours=1)
        event_ongoing = create_event("Ongoing Event", ongoing_start, ongoing_end)

        # Second event: completed (end time in past)
        completed_start = current_time - datetime.timedelta(hours=3)
        completed_end = current_time - datetime.timedelta(hours=2)
        event_completed = create_event("Completed Event", completed_start, completed_end)

        calendar_day = CalendarDay(date=test_date, timed_events=[event_ongoing, event_completed])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.pop_past_timed_event(current_time)
        assert not result  # No more events in past after removing the completed one
        assert len(scroller.timed_events) == 1
        assert scroller.timed_events[0].summary == "Ongoing Event"


class TestFirstTimedEventIsPast:
    """Tests for the first_timed_event_is_in_past helper method."""

    def test_no_events(self, test_date, current_time):
        """Test first_timed_event_is_in_past returns False when there are no events."""
        calendar_day = CalendarDay(date=test_date, timed_events=[])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.any_events_in_past(current_time)
        assert not result

    def test_with_completed_event(self, test_date, current_time):
        """Test first_timed_event_is_in_past returns True when event end_time is in the past."""
        start_time = current_time - datetime.timedelta(hours=2)
        end_time = current_time - datetime.timedelta(hours=1)
        event = create_event("Completed Event", start_time, end_time)
        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.any_events_in_past(current_time)
        assert result

    def test_with_upcoming_event(self, test_date, current_time):
        """Test first_timed_event_is_in_past returns False when event end_time is in the future."""
        start_time = current_time + datetime.timedelta(hours=1)
        end_time = current_time + datetime.timedelta(hours=2)
        event = create_event("Upcoming Event", start_time, end_time)
        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.any_events_in_past(current_time)
        assert not result

    def test_with_ongoing_event(self, test_date, current_time):
        """Test first_timed_event_is_in_past returns False for ongoing events (still in progress)."""
        start_time = current_time - datetime.timedelta(hours=1)
        end_time = current_time + datetime.timedelta(hours=1)
        event = create_event("Ongoing Event", start_time, end_time)
        calendar_day = CalendarDay(date=test_date, timed_events=[event])
        scroller = CalendarDayEventScroller(calendar_day)

        result = scroller.any_events_in_past(current_time)
        assert not result  # Event hasn't ended yet
