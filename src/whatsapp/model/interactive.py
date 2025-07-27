from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# Enums


class InteractiveType(str, Enum):
    list = "list"
    button = "button"


class InteractiveComponentType(str, Enum):
    header = "header"
    body = "body"
    footer = "footer"
    button = "button"


# Models for List Type


class InteractiveListSectionRow(BaseModel):
    id: str = Field(description="Unique ID of the row.")
    title: str = Field(description="Title of the row.")
    description: str | None = Field(
        default=None, description="Optional description of the row."
    )


class InteractiveListSection(BaseModel):
    title: str | None = Field(
        default=None, description="Optional title of the section."
    )
    rows: list[InteractiveListSectionRow] = Field(
        description="List of rows in the section."
    )


class InteractiveListAction(BaseModel):
    button: str = Field(description="Label on the list trigger button.")
    sections: list[InteractiveListSection] = Field(
        description="Sections in the interactive list."
    )


class InteractiveList(BaseModel):
    type: Literal[InteractiveType.list] = Field(description='Must be "list".')
    body: dict = Field(description="Body content for the list message.")
    action: InteractiveListAction = Field(
        description="Action containing sections and button label."
    )


# Models for Button Type


class InteractiveButtonReply(BaseModel):
    id: str = Field(description="ID to identify the button.")
    title: str = Field(description="Label shown on the button.")


class InteractiveButtonAction(BaseModel):
    buttons: list[InteractiveButtonReply] = Field(description="List of button replies.")


class InteractiveButton(BaseModel):
    type: Literal[InteractiveType.button] = Field(description='Must be "button".')
    body: dict = Field(description="Body content for the button message.")
    action: InteractiveButtonAction = Field(
        description="Action containing list of button replies."
    )


# Final Union Model


class InteractiveData(BaseModel):
    type: InteractiveType = Field(
        description="Type of interactive message, either list or button."
    )
    list: InteractiveList | None = Field(
        default=None, description="List-type interaction data."
    )
    button: InteractiveButton | None = Field(
        default=None, description="Button-type interaction data."
    )
