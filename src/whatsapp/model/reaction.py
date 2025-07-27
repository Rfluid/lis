from pydantic import BaseModel, Field


class ReactionData(BaseModel):
    message_id: str = Field(description="ID of the message to react to.")
    emoji: str = Field(description="Unicode emoji as the reaction.")
