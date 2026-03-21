import requests
from dotenv import load_dotenv
import os
from datetime import date, datetime
from collections import defaultdict

load_dotenv()

API_TOKEN = os.getenv("TODOIST_API_TOKEN")
FILTER = os.getenv("TODOIST_FILTER", "today")

EMOJIS_PRIORIDAD = {
    4: "🔴",    # p1 - Urgente
    3: "🟡",    # p2 - Alta
    2: "🔵",    # p3 - Media
    1: ""       # p4 - Normal
}

DIAS_SEMANA = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}

def fecha_a_encabezado(fecha_str):
    """Convierte una fecha ISO a un encabezado legible en español."""
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except (ValueError, TypeError):
        return "Sin fecha"
    hoy = date.today()
    diferencia = (fecha - hoy).days
    if diferencia == 0:
        return "Hoy"
    elif diferencia == 1:
        return "Mañana"
    elif diferencia == -1:
        return "Ayer"
    else:
        return DIAS_SEMANA.get(fecha.weekday(), str(fecha))

def obtener_tareas_hoy():
    """Descarga las tareas que corresponden al filtro especificado."""

    url = "https://api.todoist.com/api/v1/tasks"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"filter": FILTER}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    tareas = response.json().get('results', [])

    grupos = defaultdict(list)
    fechas_orden = []

    for tarea in tareas:
        due = tarea.get('due') or {}
        fecha_str = due.get('date', '')
        if fecha_str not in fechas_orden:
            fechas_orden.append(fecha_str)
        grupos[fecha_str].append(tarea)

    for fecha_str in fechas_orden:
        encabezado = fecha_a_encabezado(fecha_str) if fecha_str else "Sin fecha"
        print(f"## {encabezado}")
        for tarea in grupos[fecha_str]:
            prioridad = tarea.get('priority', 1)
            emoji = EMOJIS_PRIORIDAD.get(prioridad, '')
            contenido = tarea.get('content', '')
            print(f"- [ ] {emoji} {contenido}".rstrip())

if __name__ == "__main__":
    obtener_tareas_hoy()
