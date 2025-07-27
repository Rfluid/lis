import logging
from datetime import UTC, datetime, timedelta

import pytest

from src.calendar_manager import CalendarManager
from src.calendar_manager.model import DeleteEvent, UpdateEvent
from src.calendar_manager.model.create_google_event import (
    CreateGoogleCalendarEvent,
    GoogleCalendarEventDateTime,
)
from src.calendar_manager.model.update_google_event import UpdateGoogleCalendarEvent

logger = logging.getLogger(__name__)


@pytest.fixture
def calendar_manager():
    return CalendarManager()


def test_create_update_delete_event(calendar_manager):
    logger.info("=== Starting test: create, update, and delete event ===")

    # --- Prepare event data ---
    now = datetime.now(UTC)
    start_time = now + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    event_data = CreateGoogleCalendarEvent(
        summary="Test Event",
        description="Testing creation of an event",
        start=GoogleCalendarEventDateTime(
            dateTime=start_time,
            timeZone="UTC",
        ),
        end=GoogleCalendarEventDateTime(
            dateTime=end_time,
            timeZone="UTC",
        ),
    )

    # --- Create event ---
    logger.info("Creating event...")
    created_events = calendar_manager.create_events([event_data])
    created_event = created_events[0]
    event_id = created_event["id"]
    logger.info(f"Event created successfully: {event_id} ({created_event['htmlLink']})")

    assert created_event["summary"] == event_data.summary

    # --- Update event ---
    updated_summary = "Updated Test Event"
    updated_data = UpdateGoogleCalendarEvent(
        summary=updated_summary,
    )

    logger.info(f"Updating event {event_id}...")
    update = UpdateEvent(id=event_id, data=updated_data)
    updated_events = calendar_manager.update_events([update])
    updated_event = updated_events[0]
    logger.info(f"Event updated: new summary -> {updated_event['summary']}")

    assert updated_event["summary"] == updated_summary

    # --- Delete event ---
    logger.info(f"Deleting event {event_id}...")
    delete = DeleteEvent(id=event_id)
    calendar_manager.delete_events([delete])
    logger.info("Event deleted successfully.")

    logger.info("=== Test completed successfully ===")
