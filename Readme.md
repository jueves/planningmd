# Trabajar directamente con todoist_client.py
Desde la carpeta del proyecto, abrir Python y ejecutar:

```python
from todoist_client import obtener_tareas

grupos, fechas_orden = obtener_tareas()

Luego puedes inspeccionar la salida:

# Ver las fechas en orden
fechas_orden

# Ver todas las tareas de una fecha
grupos['2026-03-21']

# Ver solo los contenidos de una fecha
[t['content'] for t in grupos['2026-03-21']]

# Ver las claves disponibles en una tarea
grupos['2026-03-21'][0].keys()
```

Si el .env está en la misma carpeta, `load_dotenv()` lo carga automáticamente al importar el módulo, así que no necesitas configurar nada más.
