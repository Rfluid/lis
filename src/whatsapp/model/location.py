from pydantic import BaseModel, Field


class LocationData(BaseModel):
    latitude: float = Field(description="Latitude of the location.")
    longitude: float = Field(description="Longitude of the location.")
    name: str | None = Field(default=None, description="Name for the location.")
    address: str | None = Field(
        default=None, description="Physical address of the location."
    )
