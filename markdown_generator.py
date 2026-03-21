from datetime import datetime

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


def fecha_a_encabezado(fecha_str: str) -> str:
    """Convierte una fecha ISO a un encabezado legible en español."""
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except (ValueError, TypeError):
        return "Sin fecha"
    dia = DIAS_SEMANA.get(fecha.weekday(), str(fecha)).upper()
    return f"{dia} {fecha.strftime('%d/%m/%Y')}"


def generar_markdown(grupos: dict, fechas_orden: list) -> str:
    """Genera el texto markdown a partir de los grupos de tareas.

    Args:
        grupos: dict {fecha_str: [tareas]}
        fechas_orden: lista de fechas en orden de aparición

    Returns:
        String con el markdown generado.
    """
    lineas = []
    for fecha_str in fechas_orden:
        encabezado = fecha_a_encabezado(fecha_str) if fecha_str else "Sin fecha"
        lineas.append(f"## {encabezado}")
        for tarea in grupos[fecha_str]:
            prioridad = tarea.get('priority', 1)
            emoji = EMOJIS_PRIORIDAD.get(prioridad, '')
            contenido = tarea.get('content', '')
            lineas.append(f"- [ ] {emoji} {contenido}".rstrip())
    return "\n".join(lineas)
