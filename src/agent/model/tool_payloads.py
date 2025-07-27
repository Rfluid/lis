from pydantic import BaseModel

from src.calendar_manager.model.retrieve_events import RetrieveEvents


class ToolPayloads(BaseModel):
    search_calendars: RetrieveEvents | None = None
    rag_query: str | None = None
