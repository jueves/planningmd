from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

_CSS_PATH = Path(__file__).parent / "styles.css"


def generar_pdf_desde_html(contenido_html: str, ruta_salida: str = None, dos_columnas: bool = False) -> str:
    """Genera un PDF a partir de contenido HTML.

    Args:
        contenido_html: Fragmento HTML del body a convertir.
        ruta_salida: Ruta del archivo PDF de salida. Si no se indica,
                     se genera un nombre con la fecha/hora actual.
        dos_columnas: Si True, envuelve el contenido en un div.columnas
                      para activar el layout de dos columnas.

    Returns:
        Ruta del archivo PDF generado.
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"planning_{timestamp}.pdf"

    if dos_columnas:
        body = f'<div class="columnas">{contenido_html}</div>'
    else:
        body = contenido_html

    html_completo = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>{body}</body>
</html>"""

    HTML(string=html_completo).write_pdf(ruta_salida, stylesheets=[CSS(filename=str(_CSS_PATH))])
    return ruta_salida
