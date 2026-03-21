import markdown
from weasyprint import HTML
from datetime import datetime


CSS = """
body {
    font-family: Arial, sans-serif;
    font-size: 12pt;
    margin: 2cm;
    color: #222;
}
h2 {
    color: #2c3e50;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-top: 1.5em;
}
ul {
    list-style: none;
    padding-left: 0;
}
li {
    padding: 2px 0;
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
