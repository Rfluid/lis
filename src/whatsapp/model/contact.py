from pydantic import BaseModel, Field


class ContactName(BaseModel):
    formatted_name: str = Field(description="Full formatted name of the contact.")
    first_name: str | None = Field(
        default=None, description="First name of the contact."
    )
    last_name: str | None = Field(default=None, description="Last name of the contact.")
    middle_name: str | None = Field(
        default=None, description="Middle name of the contact."
    )


class ContactPhone(BaseModel):
    phone: str = Field(description="Phone number of the contact.")
    type: str | None = Field(default=None, description="Type of phone number.")


class ContactEmail(BaseModel):
    email: str = Field(description="Email address.")
    type: str | None = Field(default=None, description="Type of email address.")


class ContactData(BaseModel):
    name: ContactName = Field(description="Name of the contact.")
    phones: list[ContactPhone] | None = Field(
        default=None, description="Phone numbers."
    )
    emails: list[ContactEmail] | None = Field(
        default=None, description="Email addresses."
    )
