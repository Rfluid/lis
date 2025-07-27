import logging
from datetime import UTC, datetime, timedelta

import pytest

from src.calendar_manager import CalendarManager
from src.calendar_manager.model.create_google_event import (
    CreateGoogleCalendarEvent,
    GoogleCalendarEventDateTime,
)

logger = logging.getLogger(__name__)


@pytest.fixture
def calendar_manager():
    return CalendarManager()


def test_create_event_tomorrow(calendar_manager):
    tomorrow = datetime.now(UTC) + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)

    event_data = CreateGoogleCalendarEvent(
        summary="Test Meeting",
        description="Automated test for event creation.",
        start=GoogleCalendarEventDateTime(dateTime=start_time, timeZone="UTC"),
        end=GoogleCalendarEventDateTime(dateTime=end_time, timeZone="UTC"),
    )

    created_events = calendar_manager.create_events([event_data])
    created_event = created_events[0]  # get the first (and only) event

    logger.info(f"Event created: {created_event}")

    returned_start = datetime.fromisoformat(created_event["start"]["dateTime"])
    returned_end = datetime.fromisoformat(created_event["end"]["dateTime"])

    logger.info(f"Expected start: {start_time}, Returned start: {returned_start}")
    logger.info(f"Expected end: {end_time}, Returned end: {returned_end}")

    assert created_event["summary"] == event_data.summary
    assert created_event["description"] == event_data.description
    assert returned_start == start_time, "Start time mismatch"
    assert returned_end == end_time, "End time mismatch"
    assert "id" in created_event
    assert "htmlLink" in created_event
