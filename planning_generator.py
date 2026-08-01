import locale
import os
from collections import defaultdict
from todoist_client import get_tasks
from caldav_client import get_events
from markdown_generator import generate_markdown
from html_generator import generate_html, generate_section_html
from pdf_generator import generate_pdf
from quotes import get_random_quote


def generate_planning(columns: str = "2", extended_mode: bool = False):
    locale.setlocale(locale.LC_TIME, '')
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

    if extended_mode:
        title2 = os.getenv("TODOIST_TITLE2", "")
        filter2 = os.getenv("TODOIST_FILTER2", "")
        groups2, dates_order2, subtasks_by_parent2 = get_tasks(filter_query=filter2)
        html += "\n" + generate_section_html(title2, groups2, dates_order2, subtasks_by_parent2)

    path = generate_pdf(html, columns=columns)
    print(f"\nPDF generated: {path}")
    return path


if __name__ == "__main__":
    generate_planning()
