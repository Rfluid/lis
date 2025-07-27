from pydantic import BaseModel, Field

from src.whatsapp.model import UseMedia


class TemplateParameter(BaseModel):
    type: str = Field(description="Type of the parameter.")
    text: str | None = Field(default=None, description="Text of the parameter.")
    image: UseMedia | None = Field(default=None, description="Image used as parameter.")
    document: UseMedia | None = Field(
        default=None, description="Document used as parameter."
    )
    video: UseMedia | None = Field(default=None, description="Video used as parameter.")


class TemplateComponent(BaseModel):
    type: str = Field(description="Component type, such as header, body, or button.")
    parameters: list[TemplateParameter] | None = Field(
        default=None, description="List of parameters for the component."
    )


class TemplateLanguage(BaseModel):
    code: str = Field(description="Language code (e.g., en_US).")


class TemplateData(BaseModel):
    name: str = Field(description="Name of the template.")
    language: TemplateLanguage = Field(description="Language information.")
    components: list[TemplateComponent] | None = Field(
        default=None, description="Components of the template."
    )
