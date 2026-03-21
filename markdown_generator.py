import re
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


def limpiar_markdown(texto: str) -> str:
    """Elimina el formato markdown de un texto. En los enlaces conserva solo el título."""
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)  # [título](url) → título
    texto = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', texto)  # negrita/cursiva
    texto = re.sub(r'`([^`]+)`', r'\1', texto)  # código inline
    texto = re.sub(r'^#+\s*', '', texto, flags=re.MULTILINE)  # encabezados
    texto = re.sub(r'\n+', ' ', texto).strip()  # saltos de línea → espacio
    return texto


def fecha_a_encabezado(fecha_str: str) -> str:
    """Convierte una fecha ISO a un encabezado legible en español."""
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except (ValueError, TypeError):
        return "Sin fecha"
    dia = DIAS_SEMANA.get(fecha.weekday(), str(fecha)).upper()
    return f"{dia} {fecha.strftime('%d/%m/%Y')}"


def generar_markdown(grupos: dict, fechas_orden: list, modo_detalles: bool = False) -> str:
    """Genera el texto markdown a partir de los grupos de tareas.

    Args:
        grupos: dict {fecha_str: [tareas]}
        fechas_orden: lista de fechas en orden de aparición
        modo_detalles: si True, muestra nombre en negrita, etiquetas y descripción

    Returns:
        String con el markdown generado.
    """
    lineas = []
    for fecha_str in fechas_orden:
        encabezado = fecha_a_encabezado(fecha_str) if fecha_str else "Sin fecha"
        lineas.append(f"## {encabezado}")
        for tarea in sorted(grupos[fecha_str], key=lambda t: t.get('priority', 1), reverse=True):
            prioridad = tarea.get('priority', 1)
            emoji = EMOJIS_PRIORIDAD.get(prioridad, '')
            contenido = tarea.get('content', '')
            if modo_detalles:
                etiquetas = tarea.get('labels', [])
                descripcion = tarea.get('description', '') or ''
                partes = [f"**{contenido}**"]
                if etiquetas:
                    partes.append(" ".join(f"`{e}`" for e in etiquetas))
                if descripcion:
                    partes.append(limpiar_markdown(descripcion)[:100])
                lineas.append(f"- [ ] {emoji} {'  '.join(partes)}".rstrip())
            else:
                lineas.append(f"- [ ] {emoji} {contenido}".rstrip())
    return "\n".join(lineas)
