from icalendar.cal import Component
from pydantic import BaseModel, ConfigDict, field_serializer


class ToolOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    calendar_manager: dict[str, list[Component]] | None = None

    @field_serializer("calendar_manager")
    def serialize_ical_dict(
        self, cal_dict: dict[str, list[Component]] | None
    ) -> dict[str, list[str]] | None:
        if cal_dict is None:
            return None

        return {
            key: [self._serialize_component(comp) for comp in components]
            for key, components in cal_dict.items()
        }

    def _serialize_component(self, component: Component) -> str:
        """Handle both v3 and v4 of icalendar"""
        try:
            # Try v4+ method first
            if hasattr(component, "to_ics"):
                return component.to_ical().decode("utf-8")
            # Fallback to v3 method
            return component.to_ical().decode("utf-8")
        except AttributeError as e:
            raise ValueError(f"Could not serialize icalendar component: {e}")

    @classmethod
    def deserialize_ical_dict(
        cls, data: dict[str, list[str]] | None
    ) -> dict[str, list[Component]] | None:
        if data is None:
            return None

        from icalendar import Calendar

        return {
            key: [Calendar.from_ical(ics_str) for ics_str in ics_list]
            for key, ics_list in data.items()
        }
