import logging
import caldav
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta
from urllib.parse import urlparse, urlunparse
import recurring_ical_events
from icalendar import Calendar
import pytz

logger = logging.getLogger(__name__)

# Use the system's local timezone for displaying event times.
LOCAL_TZ = datetime.now().astimezone().tzinfo

load_dotenv()

ICAL_SERVER_URL = os.getenv("ICAL_SERVER_URL", "")
ICAL_USERNAME = os.getenv("ICAL_USERNAME", "")
ICAL_PASSWORD = os.getenv("ICAL_PASSWORD", "")
ICAL_CALENDAR_NAMES = os.getenv("ICAL_CALENDAR_NAMES", "")
ICAL_DAYS_AHEAD = int(os.getenv("ICAL_DAYS_AHEAD", "7"))


def _to_datetime(value, fallback: date) -> datetime:
    """Normalises a date or datetime value to a timezone-aware datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=pytz.UTC)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=pytz.UTC)
    return datetime(fallback.year, fallback.month, fallback.day, tzinfo=pytz.UTC)


def _expand_event(component, calendar_name: str, range_start: date, range_end: date) -> list[dict]:
    """Expands one iCal VEVENT component into one dict per day within the range.

    All-day events: start_time and end_time are None.
    Timed events: start_time / end_time in HH:MM (system local timezone).
    Multi-day timed events: intermediate days get 00:00 / 23:59.
    """
    dt_start_prop = component.get("DTSTART")
    dt_end_prop = component.get("DTEND") or component.get("DUE")
    if dt_start_prop is None:
        return []

    start_val = dt_start_prop.dt
    end_val = dt_end_prop.dt if dt_end_prop else start_val

    all_day = isinstance(start_val, date) and not isinstance(start_val, datetime)

    start_dt = _to_datetime(start_val, range_start)
    end_dt = _to_datetime(end_val, range_start)

    title = str(component.get("SUMMARY", ""))
    results = []
    current = start_dt.date()
    event_end_date = end_dt.date()

    # For all-day events the iCal DTEND is exclusive (e.g. a 1-day event on
    # 2026-03-22 has DTEND=2026-03-23), so we iterate while current < end_date.
    # For timed events we include the end date itself if the event ends there.
    while current < event_end_date or (not all_day and current == event_end_date):
        if range_start <= current <= range_end:
            if all_day:
                entry_start = None
                entry_end = None
            else:
                entry_start = (
                    start_dt.astimezone(LOCAL_TZ).strftime("%H:%M")
                    if current == start_dt.date()
                    else "00:00"
                )
                entry_end = (
                    end_dt.astimezone(LOCAL_TZ).strftime("%H:%M")
                    if current == end_dt.date()
                    else "23:59"
                )

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


def _resolve_caldav_url(server_url: str, username: str, password: str) -> list[str]:
    """Return candidate CalDAV base URLs to try, in priority order.

    Candidates, from highest to lowest priority:
      1. Principal URL built from server host + username, e.g.:
           https://host/dav/principals/user/<username>/
         This is the most reliable form for servers like Fastmail that
         use email-based principal paths.
      2. The URL resolved by following the /.well-known/caldav redirect
         via GET (RFC 6764). PROPFIND does not reliably follow redirects,
         so we resolve the chain manually.
      3. The server URL and well-known URL as last-resort fallbacks.
    """
    import requests as _req

    parsed = urlparse(server_url)
    base = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
    well_known = urlunparse((parsed.scheme, parsed.netloc, "/.well-known/caldav", "", "", ""))

    candidates: list[str] = []

    def _add(url: str) -> None:
        if url and url not in candidates:
            candidates.append(url)

    # 1. Explicit principal URL derived from the username (works for Fastmail
    #    and other servers that use /dav/principals/user/<email>/ paths).
    if username:
        _add(f"{base}/dav/principals/user/{username}/")

    # 2. Follow well-known and server URL redirects via GET.
    for probe_url in (well_known, server_url):
        try:
            resp = _req.get(
                probe_url,
                auth=(username, password),
                allow_redirects=True,
                timeout=10,
            )
            _add(resp.url)
        except Exception:
            pass

    # 3. Verbatim fallbacks.
    _add(server_url)
    _add(well_known)

    return candidates


def _connect(server_url: str, username: str, password: str):
    """Return (DAVClient, Principal), trying resolved CalDAV endpoint URLs."""
    candidates = _resolve_caldav_url(server_url, username, password)
    logger.debug("CalDAV endpoint candidates: %s", candidates)

    last_error: Exception = RuntimeError("No URL candidates to try.")
    for url in candidates:
        try:
            client = caldav.DAVClient(url=url, username=username, password=password)
            principal = client.principal()
            return client, principal
        except Exception as exc:
            logger.debug("Candidate %s failed: %s", url, exc)
            last_error = exc

    raise ConnectionError(
        f"Could not connect to CalDAV server at {server_url!r}. "
        f"Tried: {candidates}. Last error: {last_error}"
    ) from last_error


def get_events() -> list[dict]:
    """Connects to a CalDAV server, autodiscovers calendars, and returns events.

    Only calendars whose display name appears in ICAL_CALENDAR_NAMES are
    included. If ICAL_CALENDAR_NAMES is empty, all calendars are included.

    Returns a list of dicts sorted by date and start time, each with:
        - title       : event title
        - calendar    : calendar display name
        - date        : ISO date string (YYYY-MM-DD)
        - start_time  : "HH:MM" in system local timezone, or None for all-day events
        - end_time    : "HH:MM" in system local timezone, or None for all-day events

    Multi-day events produce one dict per day within the range.
    """
    if not ICAL_SERVER_URL:
        return []

    wanted_names = {n.strip() for n in ICAL_CALENDAR_NAMES.split(",") if n.strip()}

    today = date.today()
    range_end = today + timedelta(days=ICAL_DAYS_AHEAD)
    query_start = datetime(today.year, today.month, today.day, tzinfo=LOCAL_TZ)
    query_end = datetime(range_end.year, range_end.month, range_end.day, 23, 59, 59, tzinfo=LOCAL_TZ)

    client, principal = _connect(ICAL_SERVER_URL, ICAL_USERNAME, ICAL_PASSWORD)
    calendars = principal.calendars()

    available_names = [str(c.name or "") for c in calendars]
    logger.debug("Calendars found on server: %s", available_names)

    if wanted_names:
        missing = wanted_names - set(available_names)
        if missing:
            logger.warning(
                "ICAL_CALENDAR_NAMES contains names not found on the server: %s. "
                "Available calendars: %s",
                sorted(missing),
                available_names,
            )

    all_events: list[dict] = []

    for calendar in calendars:
        cal_name = str(calendar.name or "")
        if wanted_names and cal_name not in wanted_names:
            continue

        # Use date_search() without server-side expansion (expand=True is not
        # universally supported). recurring_ical_events handles expansion
        # client-side, which also covers VTIMEZONE and complex RRULE patterns.
        raw_objects = calendar.date_search(start=query_start, end=query_end, expand=False)

        for caldav_event in raw_objects:
            try:
                ical = Calendar.from_ical(caldav_event.data)
            except Exception as exc:
                logger.warning("Could not parse event data: %s", exc)
                continue

            for component in recurring_ical_events.of(ical).between(query_start, query_end):
                all_events.extend(_expand_event(component, cal_name, today, range_end))

    all_events.sort(key=lambda e: (e["date"], e["start_time"] or ""))
    return all_events
