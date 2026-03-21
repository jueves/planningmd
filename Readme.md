# planningmd

Generates a daily planning PDF from Todoist tasks, grouped by date.

## Requirements

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
# Required
TODOIST_API_TOKEN=your_token_here   # Todoist API token (Settings > Integrations > Developer)

# Optional
TODOIST_FILTER=today                # Todoist filter query to select tasks (default: "today")
```

## Usage

```bash
python main.py
```

Generates a PDF in the current directory and prints the markdown to the console.

## Structure

| File | Description |
|---|---|
| `main.py` | Main entry point |
| `todoist_client.py` | Fetches tasks from the Todoist API |
| `markdown_generator.py` | Generates Markdown content |
| `html_generator.py` | Converts to styled HTML |
| `pdf_generator.py` | Exports HTML to PDF (WeasyPrint) |
| `styles.css` | PDF styles |

## Working directly with todoist_client.py

From the project folder, open Python and run:

```python
from todoist_client import obtener_tareas

grupos, fechas_orden = obtener_tareas()

# See dates in order
fechas_orden

# See all tasks for a date
grupos['2026-03-21']

# See only the contents for a date
[t['content'] for t in grupos['2026-03-21']]

# See available keys in a task
grupos['2026-03-21'][0].keys()
```

If the `.env` file is in the same folder, `load_dotenv()` loads it automatically when importing the module, so no further configuration is needed.
