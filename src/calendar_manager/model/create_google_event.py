# ruff: noqa: N815
from datetime import datetime

from pydantic import BaseModel, Field


class GoogleCalendarEventDateTime(BaseModel):
    dateTime: datetime = Field(
        description="The specific date and time for the event, in RFC3339 format (e.g., '2025-04-16T15:00:00Z')."
    )
    timeZone: str | None = Field(
        default="UTC",
        description="The time zone in which the event takes place (e.g., 'America/Los_Angeles'). Defaults to 'UTC'.",
    )


class GoogleCalendarEventAttendee(BaseModel):
    email: str = Field(
        description="Email address of the attendee to invite to the event."
    )
    displayName: str | None = Field(
        default=None, description="Optional display name of the attendee."
    )
    optional: bool | None = Field(
        default=False, description="Set to True if the attendee is optional."
    )


class GoogleCalendarEventReminder(BaseModel):
    method: str = Field(
        description="Method used for the reminder. Can be 'email' or 'popup'."
    )
    minutes: int = Field(
        description="Number of minutes before the start of the event when the reminder should trigger."
    )


class GoogleCalendarGoogleCalendarEventReminders(BaseModel):
    useDefault: bool = Field(
        description="If True, uses the calendar default reminder settings. If False, uses the overrides list."
    )
    overrides: list[GoogleCalendarEventReminder] | None = Field(
        default=None,
        description="A list of custom reminders for this event, only used if useDefault is False.",
    )


class CreateGoogleCalendarEvent(BaseModel):
    summary: str = Field(
        description="Title or summary of the event that appears in the calendar."
    )
    description: str | None = Field(
        default=None, description="Full description or notes about the event."
    )
    location: str | None = Field(
        default=None,
        description="Physical or virtual location of the event (e.g., address or Zoom link).",
    )
    start: GoogleCalendarEventDateTime = Field(
        description="Start date and time of the event with timezone info."
    )
    end: GoogleCalendarEventDateTime = Field(
        description="End date and time of the event with timezone info."
    )
    reminders: GoogleCalendarGoogleCalendarEventReminders | None = Field(
        default=None, description="Custom reminder settings for the event."
    )
    colorId: str | None = Field(
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
    attendees: list[GoogleCalendarEventAttendee] | None = Field(
        default=None,
        description="List of people to invite to the event. Set None if not needed.",
    )
