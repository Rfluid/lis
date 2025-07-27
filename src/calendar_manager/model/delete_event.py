from pydantic import BaseModel, Field


class DeleteEvent(BaseModel):
    id: str = Field("ID of the event to delete.")
