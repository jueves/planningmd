import locale
import os
from collections import defaultdict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

from caldav_client import get_events
from html_generator import generate_html
from pdf_generator import generate_pdf
from quotes import get_random_quote
from todoist_client import get_tasks

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "")

app = FastAPI(title="PlanningMD API")


@app.get("/generate")
def generate(access_token: str = Query(..., description="API access token")):
    if not ACCESS_TOKEN or access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")

    locale.setlocale(locale.LC_TIME, "")

    groups, dates_order, subtasks_by_parent = get_tasks()

    events = get_events()
    events_by_date = defaultdict(list)
    for event in events:
        events_by_date[event["date"]].append(event)

    existing = set(dates_order)
    for date_str in events_by_date:
        if date_str and date_str not in existing:
            dates_order.append(date_str)
            existing.add(date_str)
    dates_order.sort(key=lambda f: f if f else "9999-99-99")

    quote = get_random_quote()
    html = generate_html(groups, dates_order, subtasks_by_parent, dict(events_by_date), quote=quote)
    path = generate_pdf(html)

    return {"path": path}
