# planningmd

Generates a daily planning PDF from Todoist tasks and CalDAV calendar events, grouped by date.

## Requirements

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
# API access token (required when using the FastAPI server)
ACCESS_TOKEN=your-secret-access-token

# Required
TODOIST_API_TOKEN=your_token_here   # Todoist API token (Settings > Integrations > Developer)

# Optional
TODOIST_FILTER=today                # Todoist filter query to select tasks (default: "today")

# CalDAV / iCal (optional — leave empty to skip calendar events)
ICAL_SERVER_URL=https://caldav.example.com
ICAL_USERNAME=user@example.com
ICAL_PASSWORD=your_password_here
ICAL_CALENDAR_NAMES=Personal,Work   # Comma-separated list; leave empty to include all calendars
ICAL_DAYS_AHEAD=7                   # Number of days ahead to fetch events (default: 7)
```

## Usage

### Script

```bash
python planning_generator.py
```

Generates a PDF in the current directory and prints the markdown to the console.

### API

```bash
uvicorn api:app --reload
```

Then call:

```
GET /generate?access_token=your-secret-access-token
```

Returns `{"status": "ok"}` and generates the PDF locally.

## Structure

| File | Description |
|---|---|
| `planning_generator.py` | Main entry point (CLI) |
| `api.py` | FastAPI server |
| `todoist_client.py` | Fetches tasks from the Todoist API |
| `caldav_client.py` | Fetches events from a CalDAV server |
| `markdown_generator.py` | Generates Markdown content |
| `html_generator.py` | Converts to styled HTML |
| `pdf_generator.py` | Exports HTML to PDF (WeasyPrint) |
| `styles.css` | PDF styles |

## Working directly with todoist_client.py

From the project folder, open Python and run:

```python
from todoist_client import get_tasks

groups, dates_order, subtasks_by_parent = get_tasks()

# See dates in order
dates_order

# See all tasks for a date
groups['2026-03-21']

# See only the contents for a date
[t['content'] for t in groups['2026-03-21']]

# See available keys in a task
groups['2026-03-21'][0].keys()

# See subtasks of a task
subtasks_by_parent[groups['2026-03-21'][0]['id']]
```

## Working directly with caldav_client.py

```python
from caldav_client import get_events

events = get_events()

# See all events
events

# See events for a specific date
[e for e in events if e['date'] == '2026-03-21']

# Available keys per event: title, calendar, date, start_time, end_time
events[0].keys()
```

If the `.env` file is in the same folder, `load_dotenv()` loads it automatically when importing either module, so no further configuration is needed.
