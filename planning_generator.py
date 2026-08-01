import locale
from collections import defaultdict
from datetime import datetime
from todoist_client import get_tasks
from caldav_client import get_events
from markdown_generator import generate_markdown
from html_generator import generate_html
from pdf_generator import generate_pdf
from qr_generator import build_created_after_url, generate_qr_svg
from quotes import get_random_quote


def generate_planning(columns: str = "2", qr: bool = False, qr_target: str = "app"):
    locale.setlocale(locale.LC_TIME, '')
    generation_time = datetime.now()
    groups, dates_order, subtasks_by_parent = get_tasks()

    events = get_events()
    events_by_date = defaultdict(list)
    for event in events:
        events_by_date[event['date']].append(event)

    # Merge event dates not already in dates_order (days with events but no tasks)
    existing = set(dates_order)
    for date_str in events_by_date:
        if date_str and date_str not in existing:
            dates_order.append(date_str)
            existing.add(date_str)
    dates_order.sort(key=lambda f: f if f else "9999-99-99")

    content = generate_markdown(groups, dates_order)
    print(content)
    quote = get_random_quote()
    html = generate_html(groups, dates_order, subtasks_by_parent, dict(events_by_date), quote=quote)
    qr_svg = generate_qr_svg(build_created_after_url(generation_time, target=qr_target)) if qr else None
    path = generate_pdf(html, columns=columns, qr_svg=qr_svg)
    print(f"\nPDF generated: {path}")
    return path


if __name__ == "__main__":
    generate_planning()
