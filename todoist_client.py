import requests
from dotenv import load_dotenv
import os
from collections import defaultdict

load_dotenv()

API_TOKEN = os.getenv("TODOIST_API_TOKEN")
FILTER = os.getenv("TODOIST_FILTER", "today")


def obtener_tareas() -> dict[str, list]:
    """Descarga las tareas que corresponden al filtro y las agrupa por fecha.

    Returns:
        Tupla (grupos, fechas_orden) donde grupos es un dict {fecha_str: [tareas]}
        y fechas_orden es la lista de fechas en el orden en que aparecieron.
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

    grupos = defaultdict(list)
    fechas_orden = []

    for tarea in tareas:
        due = tarea.get('due') or {}
        fecha_str = due.get('date', '')
        if fecha_str not in fechas_orden:
            fechas_orden.append(fecha_str)
        grupos[fecha_str].append(tarea)

    return grupos, fechas_orden
