"""Converting between the UTC text stored in the database and local time.

Every timestamp in the database is UTC text in ISO 8601 form, for example
"2027-02-15T23:05:00Z". Storing UTC means a session that crosses the change
to daylight saving time still has the right length. Convert to local time
only when showing a time to a person.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app

FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def to_text(moment):
    """Turn an aware datetime into the UTC text stored in the database."""
    return moment.astimezone(timezone.utc).strftime(FORMAT)


def from_text(text):
    """Turn stored UTC text back into an aware datetime."""
    return datetime.strptime(text, FORMAT).replace(tzinfo=timezone.utc)


def now_text():
    """The current time, as stored UTC text."""
    return to_text(datetime.now(timezone.utc))


def local_zone():
    return ZoneInfo(current_app.config["TIMEZONE"])


def local_time(text, fmt="%a %b %d, %I:%M %p"):
    """Template filter: {{ session["clock_in"] | local_time }} shows local time."""
    if not text:
        return ""
    return from_text(text).astimezone(local_zone()).strftime(fmt)
