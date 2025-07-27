from pydantic import BaseModel, Field

from src.calendar_manager.model.update_google_event import UpdateGoogleCalendarEvent


class UpdateEvent(BaseModel):
    id: str = Field(description="ID of the event to update.")
    data: UpdateGoogleCalendarEvent = Field(
        description="Data to update the event with."
    )
