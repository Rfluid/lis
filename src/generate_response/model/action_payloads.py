from pydantic import BaseModel, Field

from src.calendar_manager.model.create_google_event import CreateGoogleCalendarEvent
from src.calendar_manager.model.delete_event import DeleteEvent
from src.calendar_manager.model.update_event import UpdateEvent


class ActionPayloads(BaseModel):
    create_events: list[CreateGoogleCalendarEvent] | None = Field(
        default=None,
        description="List of events to be created. Leave None if not needed.",
    )
    delete_events: list[DeleteEvent] | None = Field(
        default=None,
        description="List of events to be deleted. Leave None if not needed.",
    )
    update_events: list[UpdateEvent] | None = Field(
        default=None,
        description="List of events to be updated. Leave None if not needed.",
    )


class ActionConfirmations(BaseModel):
    create_events: bool | None = Field(
        description="Whether the events creation is confirmed. Is None if not needed and no payload for it is provided.",
    )
    update_events: bool | None = Field(
        description="Whether the events update is confirmed. Is None if not needed and no payload for it is provided.",
    )
    delete_events: bool | None = Field(
        description="Whether the events deletion is confirmed. Is None if not needed and no payload for it is provided.",
    )
