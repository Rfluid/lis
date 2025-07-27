from typing import Any

from src.calendar_manager.model.create_google_event import CreateGoogleCalendarEvent
from src.calendar_manager.model.update_event import UpdateEvent
from src.calendar_manager.service.google import (
    create_google_event,
    delete_google_event,
    initialize_google_calendar,
    update_google_event,
)
from src.config import env


def initialize_calendar(provider: str):
    match provider:
        case "google":
            return initialize_google_calendar()
        case _:
            raise NotImplementedError(f"provider {provider} not supported")


def create_event(
    client,
    provider: str,
    calendar_id: str,
    event_data: CreateGoogleCalendarEvent,  # Use Union[] when using more providers
) -> dict[str, Any]:
    """
    Creates an event in the calendar based on the provider specified via env.
    """
    match provider:
        case "google":
            return create_google_event(client, calendar_id, event_data)
        case _:
            raise NotImplementedError(
                f"Provider '{env.CALENDAR_PROVIDER}' not supported."
            )


def delete_event(client, provider: str, calendar_id: str, event_id: str) -> None:
    match provider:
        case "google":
            return delete_google_event(client, calendar_id, event_id)
        case _:
            raise NotImplementedError(f"Provider '{provider}' not supported")


def update_event(
    client,
    provider: str,
    calendar_id: str,
    update_event: UpdateEvent,
) -> dict[str, Any]:
    match provider:
        case "google":
            return update_google_event(
                client, calendar_id, update_event.id, update_event.data
            )
        case _:
            raise NotImplementedError(f"Provider '{provider}' not supported")
