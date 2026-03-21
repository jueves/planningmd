import requests
from dotenv import load_dotenv
import os
from collections import defaultdict
from datetime import date, timedelta

load_dotenv()

API_TOKEN = os.getenv("TODOIST_API_TOKEN")
FILTER = os.getenv("TODOIST_FILTER", "today")
SUBTASK_DAYS = int(os.getenv("SUBTASK_DAYS", "7"))


def _obtener_todas_las_tareas() -> list:
    """Descarga todas las tareas activas de la cuenta sin ningún filtro."""
    url = "https://api.todoist.com/api/v1/tasks"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {}

    tareas = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tareas.extend(data.get('results', []))
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
        params = {"cursor": next_cursor}

    return tareas


def obtener_tareas() -> dict[str, list]:
    """Descarga las tareas que corresponden al filtro y las agrupa por fecha.

    Returns:
        Tupla (grupos, fechas_orden, subtareas_por_padre) donde grupos es un
        dict {fecha_str: [tareas]}, fechas_orden es la lista de fechas en orden,
        y subtareas_por_padre es un dict {parent_id: [subtareas]} con todas las
        subtareas de la cuenta.
    """
    url = "https://api.todoist.com/api/v1/tasks/filter"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"query": FILTER, "lang": "es"}

    tareas = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tareas.extend(data.get('results', []))
        next_cursor = data.get('next_cursor')
        if not next_cursor:
            break
        params = {"query": FILTER, "lang": "es", "cursor": next_cursor}

    # Construir índice de subtareas a partir de TODAS las tareas de la cuenta
    todas = _obtener_todas_las_tareas()
    subtareas_por_padre = defaultdict(list)
    for tarea in todas:
        pid = tarea.get('parent_id')
        if pid:
            subtareas_por_padre[pid].append(tarea)

    fecha_limite = date.today() + timedelta(days=SUBTASK_DAYS)

    grupos = defaultdict(list)
    fechas_orden = []

    for tarea in tareas:
        due = tarea.get('due') or {}
        fecha_str = due.get('date', '')

        if tarea.get('parent_id'):
            if not fecha_str:
                continue
            try:
                if date.fromisoformat(fecha_str) > fecha_limite:
                    continue
            except ValueError:
                continue

        if fecha_str not in fechas_orden:
            fechas_orden.append(fecha_str)
        grupos[fecha_str].append(tarea)

    fechas_orden.sort(key=lambda f: f if f else "9999-99-99")

    return grupos, fechas_orden, subtareas_por_padre
