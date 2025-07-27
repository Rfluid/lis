import logging
from datetime import UTC, datetime, timedelta

import pytest

from src.calendar_manager import CalendarManager
from src.calendar_manager.model.retrieve_events import RetrieveEvents

logger = logging.getLogger(__name__)


@pytest.fixture
def calendar_manager():
    return CalendarManager()


def test_retrieve_events_next_seven_days(calendar_manager):
    # Define the range: now to 7 days from now
    start_time = datetime.now(UTC)
    end_time = start_time + timedelta(days=7)

    payload = RetrieveEvents(start_time=start_time, end_time=end_time)

    events_by_calendar = calendar_manager.retrieve_events(payload)

    assert isinstance(events_by_calendar, dict), (
        "Expected a dictionary of events by calendar"
    )

    logger.info(f"Returned events by calendar: {events_by_calendar}")

    for calendar_url, events in events_by_calendar.items():
        logger.info(f"{calendar_url} returned {len(events)} events")

        assert isinstance(events, list), f"Expected a list of events for {calendar_url}"

        for event in events:
            logger.debug(f"Event: {event}")

            # Check that the event has start and end times (from the 'ics' Calendar)
            assert hasattr(event, "start") and hasattr(event, "end"), (
                "Event missing start or end"
            )

            event_start = event.start
            event_end = event.end

            # Check that event is within the expected time window
            assert start_time <= event_start <= end_time, (
                f"Event {event.name} is outside the time window"
            )
            assert event_start <= event_end, (
                f"Event {event.name} start is after its end"
            )

            logger.debug(f"Event {event.name} is within the time window.")
