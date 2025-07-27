from pydantic import BaseModel, Field

from src.whatsapp.model import (
    ContactData,
    ContextData,
    InteractiveData,
    LocationData,
    MessageType,
    MessagingProduct,
    OrderData,
    ReactionData,
    RecipientType,
    TemplateData,
    TextData,
    UseMedia,
)  # Se você salvou os enums em outro arquivo

# Importações dos modelos aninhados


class Message(BaseModel):
    type: MessageType = Field(
        description="Type of message being sent, such as text, image, document, etc.",
    )
    to: str = Field(description="WhatsApp ID of the message recipient.")
    messaging_product: MessagingProduct = Field(
        default=MessagingProduct.whatsapp,
        description='Messaging platform used to send the message, e.g., "whatsapp".',
    )
    recipient_type: RecipientType = Field(
        default=RecipientType.individual,
        description='Type of recipient, e.g., "individual".',
    )

    text: TextData | None = Field(
        default=None,
        description="Text message content and formatting options. Required if the message type is text.",
    )

    interactive: InteractiveData | None = Field(
        default=None,
        description="Structured interactive content such as buttons or lists. Required if the message type is interactive.",
    )

    contacts: list[ContactData] | None = Field(
        default=None,
        description="Contacts to be sent in the message. Required if the message type is contacts.",
    )

    location: LocationData | None = Field(
        default=None,
        description="Geographic location information to be shared. Required if the message type is location.",
    )

    reaction: ReactionData | None = Field(
        default=None,
        description="Reaction to a previously received message (e.g., emoji). Required if the message type is reaction.",
    )

    order: OrderData | None = Field(
        default=None,
        description="Product order information for commerce messages. Required if the message type is order.",
    )

    template: TemplateData | None = Field(
        default=None,
        description="Predefined message template structure. Required if the message type is template.",
    )

    audio: UseMedia | None = Field(
        default=None,
        description="Audio media file to send with optional caption or ID/link. Required if the message type is audio.",
    )
    video: UseMedia | None = Field(
        default=None,
        description="Video media file to send with optional caption or ID/link. Required if the message type is video.",
    )
    document: UseMedia | None = Field(
        default=None,
        description="Document media file to send with optional filename or caption. Required if the message type is document.",
    )
    sticker: UseMedia | None = Field(
        default=None,
        description="Sticker media to send. Required if the message type is sticker.",
    )
    image: UseMedia | None = Field(
        default=None,
        description="Image media to be sent with optional caption or ID/link. Required if the message type is image.",
    )

    context: ContextData | None = Field(
        default=None, description="Message context for replies or threading."
    )

    biz_opaque_callback_data: str | None = Field(
        default=None, description="Opaque metadata for message grouping or tracking."
    )

    # recipient_identity_key_hash: Optional[str] = Field(
    #     default=None,
    #     description="Hash used to verify recipient identity before sending.",
    # )
