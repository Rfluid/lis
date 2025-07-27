from pydantic import BaseModel, Field


class UseMedia(BaseModel):
    id: str | None = Field(
        default=None, description="ID of the uploaded media on the server."
    )
    link: str | None = Field(
        default=None,
        description="Direct link to media, used if media not uploaded to the server.",
    )
    caption: str | None = Field(default=None, description="Caption for the media.")
    filename: str | None = Field(
        default=None, description="Optional filename if sending document media."
    )


class TextData(BaseModel):
    preview_url: bool = Field(
        default=False,
        description="Indicates if URLs in the message should be previewed.",
    )
    body: str = Field(description="Text content of the message.")


class ButtonData(BaseModel):
    payload: str = Field(description="Custom payload returned when button is clicked.")
    text: str = Field(description="Text to show on the button.")
