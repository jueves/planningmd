import locale
from collections import defaultdict
from todoist_client import get_tasks
from caldav_client import get_events
from markdown_generator import generate_markdown
from html_generator import generate_html
from pdf_generator import generate_pdf


def main():
    locale.setlocale(locale.LC_TIME, '')
    groups, dates_order, subtasks_by_parent = get_tasks()

    events = get_events()
    events_by_date = defaultdict(list)
    for event in events:
        events_by_date[event['date']].append(event)

    content = generate_markdown(groups, dates_order)
    print(content)
    html = generate_html(groups, dates_order, subtasks_by_parent, dict(events_by_date))
    path = generate_pdf(html)
    print(f"\nPDF generated: {path}")


if __name__ == "__main__":
    main()
