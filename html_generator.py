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
    """Elimina el formato markdown de un texto usando expresiones regulares."""
    # Descripción cuyo único contenido es un enlace con título "Nota"
    if re.fullmatch(r'\[Nota\]\(.+?\)', texto.strip()):
        return ''
    # Negrita y cursiva: ***text*** o **text** o *text* o ___text___ o __text__ o _text_
    texto = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', texto)
    texto = re.sub(r'_{1,3}(.+?)_{1,3}', r'\1', texto)
    # Código inline: `text`
    texto = re.sub(r'`(.+?)`', r'\1', texto)
    # Imagen: ![alt](url) — debe ir antes que el patrón de enlace
    texto = re.sub(r'!\[.*?\]\(.+?\)', '', texto)
    # Enlace: [texto](url)
    texto = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', texto)
    # Encabezados: # texto
    texto = re.sub(r'^#{1,6}\s+', '', texto, flags=re.MULTILINE)
    # Blockquote: > texto
    texto = re.sub(r'^>\s+', '', texto, flags=re.MULTILINE)
    # Línea horizontal: --- o *** o ___
    texto = re.sub(r'^[-*_]{3,}\s*$', '', texto, flags=re.MULTILINE)
    return texto.strip()


def fecha_a_encabezado(fecha_str: str) -> str:
    """Convierte una fecha ISO a un encabezado legible en español."""
    try:
        fecha = datetime.fromisoformat(fecha_str).date()
    except (ValueError, TypeError):
        return "Sin fecha"
    dia = DIAS_SEMANA.get(fecha.weekday(), str(fecha)).upper()
    return f"{dia} {fecha.strftime('%d/%m/%Y')}"


def _escapar_html(texto: str) -> str:
    """Escapa caracteres especiales HTML."""
    return (texto
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def generar_html(grupos: dict, fechas_orden: list) -> str:
    """Genera HTML con título de tarea en negrita y descripción resumida debajo.

    Args:
        grupos: dict {fecha_str: [tareas]}
        fechas_orden: lista de fechas en orden de aparición

    Returns:
        String con el HTML generado (sin DOCTYPE/html wrapper).
    """
    partes = []
    for fecha_str in fechas_orden:
        encabezado = fecha_a_encabezado(fecha_str) if fecha_str else "Sin fecha"
        partes.append(f'<h2>{_escapar_html(encabezado)}</h2>')
        partes.append('<ul>')
        for tarea in sorted(grupos[fecha_str], key=lambda t: t.get('priority', 1), reverse=True):
            prioridad = tarea.get('priority', 1)
            emoji = EMOJIS_PRIORIDAD.get(prioridad, '')
            contenido = _escapar_html(tarea.get('content', ''))
            descripcion_raw = tarea.get('description', '') or ''
            descripcion_limpia = limpiar_markdown(descripcion_raw)[:100]
            descripcion_limpia = _escapar_html(descripcion_limpia)

            titulo_html = f'{emoji} {contenido}'.strip()
            if descripcion_limpia:
                partes.append(
                    f'<li>{titulo_html}'
                    f'<br><span class="desc">{descripcion_limpia}</span></li>'
                )
            else:
                partes.append(f'<li>{titulo_html}</li>')
        partes.append('</ul>')
    return "\n".join(partes)
