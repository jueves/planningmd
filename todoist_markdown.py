import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("TODOIST_API_TOKEN")
FILTER = os.getenv("TODOIST_FILTER", "today")

EMOJIS_PRIORIDAD = {
    4: "🔴",    # p1 - Urgente
    3: "🟡",    # p2 - Alta
    2: "🔵",    # p3 - Media
    1: ""       # p4 - Normal
}

def obtener_tareas_hoy():
    """Descarga las tareas que corresponden al filtro especificado."""
    
    url = "https://api.todoist.com/api/v1/tasks"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"filter": FILTER}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    tareas = response.json().get('items', [])
    
    for tarea in tareas:
        # Usar .get() con valor por defecto para evitar el error
        prioridad = tarea.get('priority', 1)
        emoji = EMOJIS_PRIORIDAD.get(prioridad, '')
        contenido = tarea.get('content', '')
        print(f"- [ ] {emoji} {contenido}")

if __name__ == "__main__":
    obtener_tareas_hoy()
