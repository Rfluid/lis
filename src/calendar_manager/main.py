import logging
from typing import Any

import icalendar
import recurring_ical_events
import requests
from icalendar.cal import Component

from src.calendar_manager.model import RetrieveEvents
from src.calendar_manager.model.create_google_event import CreateGoogleCalendarEvent
from src.calendar_manager.model.delete_event import DeleteEvent
from src.calendar_manager.model.update_event import UpdateEvent
from src.calendar_manager.service import initialize_calendar
from src.calendar_manager.service.main import create_event, delete_event, update_event
from src.config import env
from src.config.calendar import load_data

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


class CalendarManager:
    calendars: dict[str, str]

    def __init__(self) -> None:
        self.calendars: dict[str, str] = self._load_calendar_data()
        self.client = initialize_calendar(env.CALENDAR_PROVIDER)

    def _load_calendar_data(self) -> dict[str, str]:
        return load_data()

    def retrieve_events(
        self,
        payload: RetrieveEvents,
    ) -> dict[str, list[Component]]:
        all_events: dict[str, list[Component]] = {}

        for name, url in self.calendars.items():
            filtered_url = self.add_date_parameters(url, payload)
            events = self.fetch_ics_events(filtered_url, payload)
            all_events[name] = events  # store events by calendar name

        logging.info(
            f"retrieved all events within the time range: {payload.start_time} - {payload.end_time}"
        )

        return all_events

    def fetch_ics_events(
        self,
        calendar_url: str,
        payload: RetrieveEvents,
    ) -> list[Component]:
        try:
            response = requests.get(calendar_url)
            response.raise_for_status()

            calendar = icalendar.Calendar.from_ical(response.text)
            expanded_events = recurring_ical_events.of(calendar).between(
                payload.start_time, payload.end_time
            )

            return expanded_events

        except Exception as e:
            logger.error(f"Error fetching calendar from {calendar_url}: {str(e)}")
            raise RuntimeError(f"Failed to fetch calendar: {str(e)}") from e

    def create_events(
        self,
        events_data: list[
            CreateGoogleCalendarEvent
        ],  # Use Union[] when using more providers
    ) -> list[dict[str, Any]]:
        """
        Creates multiple events in the calendar.
        """
        return [
            create_event(self.client, env.CALENDAR_PROVIDER, env.CALENDAR_ID, data)
            for data in events_data
        ]

    def delete_events(self, events: list[DeleteEvent]) -> None:
        """
        Deletes multiple events from the calendar by their IDs.
        """
        for data in events:
            delete_event(self.client, env.CALENDAR_PROVIDER, env.CALENDAR_ID, data.id)

    def update_events(self, events: list[UpdateEvent]) -> list[dict[str, Any]]:
        """
        Updates multiple events in the calendar.
        """
        return [
            update_event(self.client, env.CALENDAR_PROVIDER, env.CALENDAR_ID, data)
            for data in events
        ]

    def add_date_parameters(
        self,
        calendar_url: str,
        payload: RetrieveEvents,
    ) -> str:
        iso_format = payload.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        google_format_start = payload.start_time.strftime("%Y%m%dT%H%M%SZ")
        google_format_end = payload.end_time.strftime("%Y%m%dT%H%M%SZ")

        separator = "&" if "?" in calendar_url else "?"

        if "google.com" in calendar_url or "googleapis.com" in calendar_url:
            return f"{calendar_url}{separator}start-min={google_format_start}&start-max={google_format_end}"
        elif "outlook.live.com" in calendar_url or "outlook.office.com" in calendar_url:
            return f"{calendar_url}{separator}startDateTime={iso_format}&endDateTime={payload.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        elif "apple.com" in calendar_url or "icloud.com" in calendar_url:
            return f"{calendar_url}{separator}filter=start:{google_format_start},end:{google_format_end}"
        else:
            logger.warning(
                f"Unknown calendar provider for URL: {calendar_url}. No date filtering applied."
            )
            return calendar_url
