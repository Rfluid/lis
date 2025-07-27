import os

# Calendar to schedule events
CALENDAR_PROVIDER = os.getenv(
    "CALENDAR_PROVIDER", "google"
)  # "google", "outlook", etc.
CALENDAR_ID = os.getenv("CALENDAR_ID", "lis")  # email or calendar ID
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE",
    "service-account.google.json",
)  # path to credentials
