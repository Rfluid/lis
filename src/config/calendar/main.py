import json

from src.config import env


def load_data() -> dict[str, str]:
    path = env.DATA_DIR / "calendars.json"
    with open(path, encoding="utf-8") as f:
        calendar_list = json.load(f)
    return {
        calendar["name"]: calendar["url"]
        for calendar in calendar_list
        if "name" in calendar and "url" in calendar
    }
