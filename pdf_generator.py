import markdown
from weasyprint import HTML
from datetime import datetime


CSS = """
body {
    font-family: Arial, sans-serif;
    font-size: 9pt;
    margin: 0.5cm;
    color: #222;
}
h2 {
    color: #2c3e50;
    border-bottom: 1px solid #ccc;
    padding-bottom: 2px;
    margin-top: 0.6em;
    margin-bottom: 0.2em;
    font-size: 11pt;
}
ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
}
li {
    padding: 1px 0;
}
.desc {
    font-size: 7pt;
    color: #555;
    margin-left: 1.2em;
}
"""


def generar_pdf(contenido_markdown: str, ruta_salida: str = None) -> str:
    """Genera un PDF a partir de contenido markdown.

    Args:
        contenido_markdown: String con el markdown a convertir.
        ruta_salida: Ruta del archivo PDF de salida. Si no se indica,
                     se genera un nombre con la fecha/hora actual.

    Returns:
        Ruta del archivo PDF generado.
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"planning_{timestamp}.pdf"

    md = contenido_markdown.replace('- [ ] ', '- ')
    html_body = markdown.markdown(md, extensions=['extra'])
    html_completo = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>{html_body}</body>
</html>"""

    HTML(string=html_completo).write_pdf(ruta_salida)
    return ruta_salida


def generar_pdf_desde_html(contenido_html: str, ruta_salida: str = None) -> str:
    """Genera un PDF a partir de contenido HTML.

    Args:
        contenido_html: Fragmento HTML del body a convertir.
        ruta_salida: Ruta del archivo PDF de salida. Si no se indica,
                     se genera un nombre con la fecha/hora actual.

    Returns:
        Ruta del archivo PDF generado.
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"planning_{timestamp}.pdf"

    html_completo = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>{contenido_html}</body>
</html>"""

    HTML(string=html_completo).write_pdf(ruta_salida)
    return ruta_salida
