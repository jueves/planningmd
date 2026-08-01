from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

_CSS_PATH = Path(__file__).parent / "styles.css"
_OUTPUT_DIR = Path(__file__).parent / "pdfs"


def _complete_html(html_content: str, two_columns: bool, qr_svg: str = None) -> str:
    if qr_svg:
        html_content = f'<div class="qr-float">{qr_svg}</div>{html_content}'
    body = f'<div class="columnas">{html_content}</div>' if two_columns else html_content
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>{body}</body>
</html>"""


def generate_pdf(html_content: str, output_path: str = None, columns: str = "2", qr_svg: str = None) -> str:
    """Generates a PDF from HTML content.

    Args:
        html_content: HTML fragment of the body to convert.
        output_path: Path of the output PDF file. If not provided,
                     a name with the current date/time is generated
                     inside the pdfs/ directory.
        columns: Layout mode. "2" (default) forces the two-column layout,
                 "1" forces a single column, and "auto" renders a single
                 column first and re-renders with two columns if the
                 result takes more than one page.
        qr_svg: Optional SVG string with a QR code floated at the top
                right of the content, with the text flowing around it.

    Returns:
        Path of the generated PDF file.
    """
    if columns not in ("auto", "1", "2"):
        raise ValueError(f"Invalid columns mode: {columns!r} (expected 'auto', '1' or '2')")

    if output_path is None:
        _OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(_OUTPUT_DIR / f"planning_{timestamp}.pdf")

    ts = datetime.now().strftime('%d/%m/%Y  %H:%M')
    footer_css = CSS(string=f"""
        @page {{
            @bottom-center {{
                font-family: Arial, sans-serif;
                font-size: 6pt;
                color: #bbb;
                content: "{ts}";
            }}
        }}
    """)
    styles = [CSS(filename=str(_CSS_PATH)), footer_css]

    if columns == "2":
        HTML(string=_complete_html(html_content, two_columns=True, qr_svg=qr_svg)).write_pdf(
            output_path, stylesheets=styles
        )
        return output_path

    document = HTML(string=_complete_html(html_content, two_columns=False, qr_svg=qr_svg)).render(
        stylesheets=styles
    )
    if columns == "auto" and len(document.pages) > 1:
        print(f"PDF has {len(document.pages)} pages, regenerating with two columns...")
        HTML(string=_complete_html(html_content, two_columns=True, qr_svg=qr_svg)).write_pdf(
            output_path, stylesheets=styles
        )
    else:
        document.write_pdf(output_path)

    return output_path
