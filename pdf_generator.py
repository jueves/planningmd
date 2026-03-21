from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

_CSS_PATH = Path(__file__).parent / "styles.css"


def _html_completo(contenido_html: str, dos_columnas: bool) -> str:
    body = f'<div class="columnas">{contenido_html}</div>' if dos_columnas else contenido_html
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>{body}</body>
</html>"""


def generar_pdf_desde_html(contenido_html: str, ruta_salida: str = None, dos_columnas: bool = False) -> str:
    """Genera un PDF a partir de contenido HTML.

    Si dos_columnas es False (por defecto), renderiza primero sin columnas y
    comprueba el número de páginas. Si el resultado ocupa más de una página,
    vuelve a renderizar automáticamente con dos columnas.

    Args:
        contenido_html: Fragmento HTML del body a convertir.
        ruta_salida: Ruta del archivo PDF de salida. Si no se indica,
                     se genera un nombre con la fecha/hora actual.
        dos_columnas: Si True, usa el layout de dos columnas directamente.

    Returns:
        Ruta del archivo PDF generado.
    """
    if ruta_salida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"planning_{timestamp}.pdf"

    estilos = [CSS(filename=str(_CSS_PATH))]

    if dos_columnas:
        HTML(string=_html_completo(contenido_html, dos_columnas=True)).write_pdf(
            ruta_salida, stylesheets=estilos
        )
        return ruta_salida

    documento = HTML(string=_html_completo(contenido_html, dos_columnas=False)).render(
        stylesheets=estilos
    )
    if len(documento.pages) > 1:
        print(f"PDF ocupa {len(documento.pages)} páginas, regenerando con dos columnas...")
        HTML(string=_html_completo(contenido_html, dos_columnas=True)).write_pdf(
            ruta_salida, stylesheets=estilos
        )
    else:
        documento.write_pdf(ruta_salida)

    return ruta_salida
