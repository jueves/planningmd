# planningmd

Genera un PDF de planificación diaria a partir de las tareas de Todoist, agrupadas por fecha.

## Requisitos

```bash
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto con tu token de Todoist:

```
TODOIST_API_TOKEN=tu_token_aqui
```

## Uso

```bash
python main.py
```

Genera el PDF en el directorio actual e imprime el markdown en consola.

## Estructura

| Archivo | Descripción |
|---|---|
| `main.py` | Punto de entrada principal |
| `todoist_client.py` | Obtiene tareas de la API de Todoist |
| `markdown_generator.py` | Genera el contenido en Markdown |
| `html_generator.py` | Convierte a HTML con estilos |
| `pdf_generator.py` | Exporta el HTML a PDF (WeasyPrint) |
| `styles.css` | Estilos del PDF |

## Trabajar directamente con todoist_client.py

Desde la carpeta del proyecto, abrir Python y ejecutar:

```python
from todoist_client import obtener_tareas

grupos, fechas_orden = obtener_tareas()

# Ver las fechas en orden
fechas_orden

# Ver todas las tareas de una fecha
grupos['2026-03-21']

# Ver solo los contenidos de una fecha
[t['content'] for t in grupos['2026-03-21']]

# Ver las claves disponibles en una tarea
grupos['2026-03-21'][0].keys()
```

Si el `.env` está en la misma carpeta, `load_dotenv()` lo carga automáticamente al importar el módulo, así que no necesitas configurar nada más.
