from pydantic import BaseModel, Field


class ContextData(BaseModel):
    message_id: str = Field(description="ID of the message being replied to.")
    from_id: str | None = Field(
        default=None, description="Sender ID of the original message."
    )
