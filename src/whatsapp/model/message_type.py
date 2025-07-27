from enum import Enum


class MessageType(str, Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    document = "document"
    sticker = "sticker"
    interactive = "interactive"
    template = "template"
    contacts = "contacts"
    location = "location"
    reaction = "reaction"
    order = "order"
    button = "button"
