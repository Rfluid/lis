from datetime import datetime

from pydantic import BaseModel, Field


class RetrieveEvents(BaseModel):
    start_time: datetime = Field(
        description="The start time for the event retrieval. Must be in ISO format.",
    )
    end_time: datetime = Field(
        description="The end time for the event retrieval. Must be in ISO format.",
    )
