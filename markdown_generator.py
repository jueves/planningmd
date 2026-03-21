from datetime import datetime

PRIORITY_EMOJIS = {
    4: "🔴",    # p1 - Urgent
    3: "🟡",    # p2 - High
    2: "🔵",    # p3 - Medium
    1: ""       # p4 - Normal
}

WEEKDAYS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def date_to_heading(date_str: str) -> str:
    """Converts an ISO date to a readable heading."""
    try:
        date = datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        return "No date"
    day = WEEKDAYS.get(date.weekday(), str(date)).upper()
    return f"{day} {date.strftime('%d/%m/%Y')}"


def generate_markdown(groups: dict, dates_order: list) -> str:
    """Generates markdown text from the task groups.

    Args:
        groups: dict {date_str: [tasks]}
        dates_order: list of dates in order of appearance

    Returns:
        String with the generated markdown.
    """
    lines = []
    for date_str in dates_order:
        heading = date_to_heading(date_str) if date_str else "No date"
        lines.append(f"## {heading}")
        for task in sorted(groups[date_str], key=lambda t: t.get('priority', 1), reverse=True):
            priority = task.get('priority', 1)
            emoji = PRIORITY_EMOJIS.get(priority, '')
            content = task.get('content', '')
            lines.append(f"- [ ] {emoji} {content}".rstrip())
    return "\n".join(lines)
