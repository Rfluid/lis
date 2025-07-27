from pydantic import BaseModel, Field

from src.calendar_manager.model.create_google_event import (
    GoogleCalendarEventAttendee,
    GoogleCalendarEventDateTime,
    GoogleCalendarGoogleCalendarEventReminders,
)


class UpdateGoogleCalendarEvent(BaseModel):
    summary: str | None = Field(
        default=None,
        description="Title or summary of the event that appears in the calendar.",
    )
    description: str | None = Field(
        default=None, description="Full description or notes about the event."
    )
    location: str | None = Field(
        default=None,
        description="Physical or virtual location of the event (e.g., address or Zoom link).",
    )
    start: GoogleCalendarEventDateTime | None = Field(
        default=None, description="Start date and time of the event with timezone info."
    )
    end: GoogleCalendarEventDateTime | None = Field(
        default=None, description="End date and time of the event with timezone info."
    )
    attendees: list[GoogleCalendarEventAttendee] | None = Field(
        default=None, description="List of people to invite to the event."
    )
    reminders: GoogleCalendarGoogleCalendarEventReminders | None = Field(
        default=None, description="Custom reminder settings for the event."
    )
    colorId: str | None = Field(  # noqa: N815
        default=None,
        description="ID of the color to use for the event (e.g., '1' for blue, '11' for red).",
    )
    visibility: str | None = Field(
        default=None,
        description="Visibility of the event. Can be 'default', 'public', 'private', or 'confidential'.",
    )
    transparency: str | None = Field(
        default="opaque",
        description="Indicates whether the event blocks time on the calendar. Use 'opaque' to block or 'transparent' to not block.",
    )
