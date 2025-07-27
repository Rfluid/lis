import logging
from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from src.calendar_manager.model.create_google_event import CreateGoogleCalendarEvent
from src.calendar_manager.model.update_google_event import UpdateGoogleCalendarEvent
from src.common import remove_none_values
from src.config import env


def initialize_google_calendar():
    try:
        creds = Credentials.from_service_account_file(
            env.DATA_DIR / env.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/calendar"],
            # subject="ruy.vieiraneto@gmail.com", # You might want to set this correctly if you need to invite attendees.
        )
        service = build("calendar", "v3", credentials=creds)
        logging.info("Google Calendar service initialized successfully.")

        return service
    except Exception as e:
        logging.error(f"Failed to initialize Google Calendar API: {e}")
        raise


def create_google_event(
    client,
    calendar_id: str,
    event_data: CreateGoogleCalendarEvent,
) -> dict[str, Any]:
    """
    Creates an event in the Google Calendar using the provided client and calendar ID.

    Args:
        client: The initialized Google Calendar service client.
        calendar_id: ID of the calendar to insert the event into.
        event_data: Pydantic model containing event details.

    Returns:
        The created event resource as a dictionary.
    """

    try:
        raw_body = event_data.model_dump(mode="json")
        body = remove_none_values(raw_body)

        logging.info(f"Creating event in calendar '{calendar_id}' with data: {body}")
        event = client.events().insert(calendarId=calendar_id, body=body).execute()
        logging.info(f"Event created successfully: {event.get('htmlLink')}")
        return event
    except Exception:
        logging.exception("Failed to create event …")
        raise


def delete_google_event(client, calendar_id: str, event_id: str) -> None:
    """
    Deletes an event by ID from the given calendar.
    """
    try:
        # Convert the google uid to the event id if needed
        if "@" in event_id:
            event_id = event_id.split("@")[0]

        client.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        logging.info(f"Event {event_id} deleted successfully.")
    except Exception as e:
        logging.error(f"Failed to delete event '{event_id}': {e}")
        raise


def update_google_event(
    client,
    calendar_id: str,
    event_id: str,
    data: UpdateGoogleCalendarEvent,
) -> dict[str, Any]:
    """
    Updates an existing event in Google Calendar.

    Args:
        client: Google Calendar API client.
        calendar_id: Calendar ID.
        event_id: Event ID to update.
        data: Pydantic model containing updated event details.

    Returns:
        The updated event object.
    """
    try:
        # Convert the google uid to the event id if needed
        if "@" in event_id:
            event_id = event_id.split("@")[0]

        # Retrieve the existing event
        event = client.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Update the event with new data
        update_data = remove_none_values(
            data.model_dump(
                exclude_unset=True,
                mode="json",
            )
        )
        logging.info(f"Event is: {event}, update data is: {update_data}")
        for key, value in update_data.items():
            event[key] = value

        event = remove_none_values(event)

        logging.info(f"Will update the event '{event_id}' with data: {event}")

        # Update the event
        updated_event = (
            client.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        logging.info(
            f"Event '{event_id}' updated successfully: {updated_event.get('htmlLink')}"
        )
        return updated_event
    except Exception as e:
        logging.error(
            f"Failed to update event '{event_id}' in calendar '{calendar_id}': {e}"
        )
        raise
