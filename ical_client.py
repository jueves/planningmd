import requests
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta, time
import recurring_ical_events
from icalendar import Calendar
import pytz

load_dotenv()

ICAL_USERNAME = os.getenv("ICAL_USERNAME", "")
ICAL_PASSWORD = os.getenv("ICAL_PASSWORD", "")
ICAL_URLS = os.getenv("ICAL_URLS", "")
ICAL_DAYS_AHEAD = int(os.getenv("ICAL_DAYS_AHEAD", "7"))


def _fetch_calendar(url: str) -> Calendar:
    """Downloads and parses an iCal file from a URL with optional HTTP auth."""
    auth = (ICAL_USERNAME, ICAL_PASSWORD) if ICAL_USERNAME else None
    response = requests.get(url, auth=auth, timeout=30)
    response.raise_for_status()
    return Calendar.from_ical(response.content)


def _calendar_name(cal: Calendar, url: str) -> str:
    """Extracts the calendar name from X-WR-CALNAME or falls back to the URL."""
    name = cal.get("X-WR-CALNAME")
    if name:
        return str(name)
    # Use the last path segment of the URL, without the .ics extension
    path = url.rstrip("/").split("/")[-1]
    return path.replace(".ics", "") or url


def _to_datetime(value, default_date: date) -> datetime:
    """Normalises a date or datetime value to a timezone-aware datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=pytz.UTC)
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=pytz.UTC)
    return datetime(default_date.year, default_date.month, default_date.day, tzinfo=pytz.UTC)


def _expand_event(event, calendar_name: str, range_start: date, range_end: date) -> list[dict]:
    """Expands a single event into one dict per day it occupies within the range.

    All-day events have start/end time as None.
    Timed events carry their actual start and end times on each day entry.
    """
    dt_start = event.get("DTSTART")
    dt_end = event.get("DTEND") or event.get("DUE")
    if dt_start is None:
        return []

    start_val = dt_start.dt
    end_val = dt_end.dt if dt_end else start_val

    all_day = isinstance(start_val, date) and not isinstance(start_val, datetime)

    start_dt = _to_datetime(start_val, range_start)
    end_dt = _to_datetime(end_val, range_start)

    # For all-day events the end date in iCal is exclusive, keep it as-is for
    # iteration; for timed events we use the actual start/end times.
    title = str(event.get("SUMMARY", ""))

    results = []
    current = start_dt.date()
    event_end_date = end_dt.date()

    while current < event_end_date or (current == event_end_date and not all_day):
        if range_start <= current <= range_end:
            if all_day:
                entry_start = None
                entry_end = None
            else:
                # On the first day use the real start time; on subsequent days 00:00.
                if current == start_dt.date():
                    entry_start = start_dt.astimezone(pytz.UTC).strftime("%H:%M")
                else:
                    entry_start = "00:00"
                # On the last day use the real end time; on earlier days 23:59.
                if current == end_dt.date():
                    entry_end = end_dt.astimezone(pytz.UTC).strftime("%H:%M")
                else:
                    entry_end = "23:59"

            results.append({
                "title": title,
                "calendar": calendar_name,
                "date": current.isoformat(),
                "start_time": entry_start,
                "end_time": entry_end,
            })

        current += timedelta(days=1)
        if current > range_end:
            break

    return results


def get_events() -> list[dict]:
    """Returns a list of event dicts for the configured date range.

    Each dict contains:
        - title: event title
        - calendar: calendar name
        - date: ISO date string (YYYY-MM-DD)
        - start_time: "HH:MM" in UTC (None for all-day events)
        - end_time: "HH:MM" in UTC (None for all-day events)

    Multi-day events produce one dict per day within the range.
    """
    urls = [u.strip() for u in ICAL_URLS.split(",") if u.strip()]
    if not urls:
        return []

    today = date.today()
    range_end = today + timedelta(days=ICAL_DAYS_AHEAD)

    # recurring_ical_events expects datetime objects
    query_start = datetime(today.year, today.month, today.day, tzinfo=pytz.UTC)
    query_end = datetime(range_end.year, range_end.month, range_end.day, 23, 59, 59, tzinfo=pytz.UTC)

    all_events: list[dict] = []

    for url in urls:
        cal = _fetch_calendar(url)
        name = _calendar_name(cal, url)
        events = recurring_ical_events.of(cal).between(query_start, query_end)
        for event in events:
            all_events.extend(_expand_event(event, name, today, range_end))

    all_events.sort(key=lambda e: (e["date"], e["start_time"] or ""))

    return all_events
