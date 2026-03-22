import re
from datetime import datetime

PRIORITY_EMOJIS = {
    4: "🔴",    # p1 - Urgent
    3: "🟡",    # p2 - High
    2: "🔵",    # p3 - Medium
    1: ""       # p4 - Normal
}

def clean_markdown(text: str) -> str:
    """Removes markdown formatting from text using regular expressions."""
    # Description whose only content is a link with title "Note"
    if re.fullmatch(r'\[Note\]\(.+?\)', text.strip()):
        return ''
    # Bold and italic: ***text*** or **text** or *text* or ___text___ or __text__ or _text_
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.+?)_{1,3}', r'\1', text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Image: ![alt](url) — must come before the link pattern
    text = re.sub(r'!\[.*?\]\(.+?\)', '', text)
    # Link: [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # Headings: # text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Blockquote: > text
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Horizontal rule: --- or *** or ___
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def date_to_heading(date_str: str) -> str:
    """Converts an ISO date to a readable heading."""
    try:
        date = datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        return "No date"
    day = date.strftime('%A').upper()
    return f"{day} {date.strftime('%d/%m/%Y')}"


def _escape_html(text: str) -> str:
    """Escapes HTML special characters."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def generate_html(groups: dict, dates_order: list, subtasks_by_parent: dict = None, events_by_date: dict = None) -> str:
    """Generates HTML with task title, summarized description and subtasks below.

    Args:
        groups: dict {date_str: [tasks]}
        dates_order: list of dates in order of appearance
        subtasks_by_parent: dict {parent_id: [subtasks]} with ALL subtasks
        events_by_date: dict {date_str: [events]} with calendar events

    Returns:
        String with the generated HTML (without DOCTYPE/html wrapper).
    """
    if subtasks_by_parent is None:
        subtasks_by_parent = {}
    if events_by_date is None:
        events_by_date = {}

    blocks = []
    for date_str in dates_order:
        heading = date_to_heading(date_str) if date_str else "No date"
        parts = [f'<h2>{_escape_html(heading)}</h2>', '<ul>']

        # Render calendar events before tasks
        for event in events_by_date.get(date_str, []):
            title = _escape_html(event.get('title', ''))
            calendar = _escape_html(event.get('calendar', ''))
            start_time = event.get('start_time')
            end_time = event.get('end_time')
            if start_time and end_time:
                time_range = f"De {start_time} a {end_time}"
                meta = f"{calendar} &mdash; {time_range}" if calendar else time_range
            else:
                meta = calendar
            meta_html = f'<br><span class="event-meta">{meta}</span>' if meta else ''
            parts.append(f'<li class="event">{title}{meta_html}</li>')

        parent_tasks = [t for t in groups[date_str] if not t.get('parent_id')]
        for task in sorted(parent_tasks, key=lambda t: t.get('priority', 1), reverse=True):
            priority = task.get('priority', 1)
            emoji = PRIORITY_EMOJIS.get(priority, '')
            content = _escape_html(task.get('content', ''))
            raw_description = task.get('description', '') or ''
            clean_description = clean_markdown(raw_description)[:100]
            clean_description = _escape_html(clean_description)

            title_html = f'{emoji} {content}'.strip()
            extra = ''
            if clean_description:
                extra += f'<br><span class="desc">{clean_description}</span>'

            subtasks = subtasks_by_parent.get(task.get('id'), [])
            if subtasks:
                items = ''.join(
                    f'<li>{_escape_html(s.get("content", ""))}</li>'
                    for s in subtasks
                )
                extra += f'<ul class="subtasks">{items}</ul>'

            parts.append(f'<li>{title_html}{extra}</li>')
        parts.append('</ul>')
        blocks.append("\n".join(parts))
    return "\n".join(blocks)
