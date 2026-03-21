import requests
from dotenv import load_dotenv
import os
from collections import defaultdict
from datetime import date, timedelta

load_dotenv()

API_TOKEN = os.getenv("TODOIST_API_TOKEN")
FILTER = os.getenv("TODOIST_FILTER", "today")
SUBTASK_DAYS = int(os.getenv("SUBTASK_DAYS", "7"))


def _get_all_tasks() -> list:
    """Downloads all active tasks from the account without any filter."""
    url = "https://api.todoist.com/api/v1/tasks"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {}

    tasks = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tasks.extend(data.get('results', []))
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
        params = {"cursor": next_cursor}

    return tasks


def get_tasks() -> dict[str, list]:
    """Downloads the tasks matching the filter and groups them by date.

    Returns:
        Tuple (groups, dates_order, subtasks_by_parent) where groups is a
        dict {date_str: [tasks]}, dates_order is the list of dates in order,
        and subtasks_by_parent is a dict {parent_id: [subtasks]} with all
        subtasks in the account.
    """
    url = "https://api.todoist.com/api/v1/tasks/filter"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"query": FILTER, "lang": "en"}

    tasks = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tasks.extend(data.get('results', []))
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
        params = {"query": FILTER, "lang": "en", "cursor": next_cursor}

    # Build subtask index from ALL tasks in the account
    all_tasks = _get_all_tasks()
    subtasks_by_parent = defaultdict(list)
    for task in all_tasks:
        pid = task.get('parent_id')
        if pid:
            subtasks_by_parent[pid].append(task)

    date_limit = date.today() + timedelta(days=SUBTASK_DAYS)

    groups = defaultdict(list)
    dates_order = []

    for task in tasks:
        due = task.get('due') or {}
        date_str = due.get('date', '')

        if task.get('parent_id'):
            if not date_str:
                continue
            try:
                if date.fromisoformat(date_str) > date_limit:
                    continue
            except ValueError:
                continue

        if date_str not in dates_order:
            dates_order.append(date_str)
        groups[date_str].append(task)

    dates_order.sort(key=lambda f: f if f else "9999-99-99")

    return groups, dates_order, subtasks_by_parent
