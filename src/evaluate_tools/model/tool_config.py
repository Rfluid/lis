from typing import Literal

from pydantic import BaseModel, Field

from src.agent.model.steps import Steps
from src.calendar_manager.model.retrieve_events import RetrieveEvents
from src.generate_response.model.action_payloads import ActionPayloads
from src.whatsapp.model.message import Message


class ToolConfig(BaseModel):
    search_calendars: RetrieveEvents | None = Field(
        default=None,
        description=f"The payload to be sent to the calendar manager tool to search all events between two dates. Used to retrieve events. Is required if the tool set is ${Steps.search_calendars}.",
    )
    rag_query: str | None = Field(
        default=None,
        description="The query to be sent to the RAG tool. Used to retrieve information from the RAG tool.",
    )
    tool: Literal[
        "search_calendars",
        "get_current_date",
        "rag",
        "generate_response",
    ] = Field(
        description="The tool that the agent needs to use to retrieve the necessary information."
    )
    # reason: str = Field(description="The reason why the agent needs to use this tool.")


class BaseToolConfigWithResponse(BaseModel):
    search_calendars: RetrieveEvents | None = Field(
        default=None,
        description=f"The payload to be sent to the calendar manager tool to search all events between two dates. Used to retrieve events. Is required if the tool set is ${Steps.search_calendars}.",
    )
    action_payloads: ActionPayloads | None = Field(
        default=None,
        description="Payloads for the actions to be performed. This will contain the data to create, update or delete events.",
    )
    rag_query: str | None = Field(
        default=None,
        description="The query to be sent to the RAG tool. Used to retrieve information from the RAG tool.",
    )
    tool: Literal[
        "get_current_date",
        "search_calendars",
        "modify_calendar",
        "rag",
        "end",
    ] = Field(
        description="The tool that the agent needs to use to retrieve the necessary information."
    )
    # reason: str = Field(description="The reason why the agent needs to use this tool.")


class ToolConfigWithResponse(BaseToolConfigWithResponse):
    response: str | None = Field(description="LLM's text response to the input query.")


class ToolConfigWithWhatsAppResponse(BaseToolConfigWithResponse):
    data: Message | None = Field(description="Response in the WhatsApp format.")
