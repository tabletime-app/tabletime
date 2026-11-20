"""Converting between the UTC text stored in the database and local time.

Every timestamp in the database is UTC text in ISO 8601 form, for example
"2027-02-15T23:05:00Z". Storing UTC means a session that crosses the change
to daylight saving time still has the right length. Convert to local time
only when showing a time to a person.

Get the current time only from utc_now(). Tests replace that one function to
fix the clock (see the freeze_time fixture in tests/conftest.py), so code
that calls datetime.now() directly can't be tested at a chosen moment.
Import the module and call times.utc_now(), as in

    from .. import times
    start, end = times.week_bounds(times.utc_now())

rather than `from ..times import utc_now`, which keeps a copy of the real
function that the test clock can't replace. now_text() and week_bounds()
already use the test clock.
"""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import current_app

FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def to_text(moment):
    """Turn an aware datetime into the UTC text stored in the database."""
    return moment.astimezone(timezone.utc).strftime(FORMAT)


def from_text(text):
    """Turn stored UTC text back into an aware datetime."""
    return datetime.strptime(text, FORMAT).replace(tzinfo=timezone.utc)


def utc_now():
    """The current time as an aware datetime in UTC. Tests replace this to fix the clock."""
    return datetime.now(timezone.utc)


def now_text():
    """The current time, as stored UTC text."""
    return to_text(utc_now())


def local_zone():
    return ZoneInfo(current_app.config["TIMEZONE"])


def local_time(text, fmt="%a %b %d, %I:%M %p"):
    """Template filter: {{ session["clock_in"] | local_time }} shows local time."""
    if not text:
        return ""
    return from_text(text).astimezone(local_zone()).strftime(fmt)


def week_bounds(moment=None):
    """The study week containing moment (now by default): Monday 00:00 to the next Monday 00:00, local time.

    Returns (start, end) as stored UTC text, ready for a query such as
    clock_in >= ? AND clock_in < ?. The boundaries are found in local time
    first, because "Monday" means Monday where the study table is, and then
    converted to UTC, where local midnight is 5 or 6 am depending on daylight
    saving time.
    """
    zone = local_zone()
    local = (moment or utc_now()).astimezone(zone)
    monday = local.date() - timedelta(days=local.weekday())
    start = datetime.combine(monday, time(0, 0), zone)
    end = datetime.combine(monday + timedelta(days=7), time(0, 0), zone)
    return to_text(start), to_text(end)


def minutes_between(start_text, end_text):
    """Whole minutes from one stored time to another."""
    return int((from_text(end_text) - from_text(start_text)).total_seconds() // 60)


def from_form(value):
    """Turn a form's datetime-local value such as "2027-02-15T18:30", in local time, into stored UTC text."""
    local = datetime.strptime(value, "%Y-%m-%dT%H:%M").replace(tzinfo=local_zone())
    return to_text(local)


def to_form(text):
    """Template filter: turn stored UTC text into a value for <input type="datetime-local">.

    {{ s["clock_in"] | to_form }}
    """
    if not text:
        return ""
    return from_text(text).astimezone(local_zone()).strftime("%Y-%m-%dT%H:%M")
