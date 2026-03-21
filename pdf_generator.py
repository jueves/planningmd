from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

_CSS_PATH = Path(__file__).parent / "styles.css"


def _complete_html(html_content: str, two_columns: bool) -> str:
    body = f'<div class="columnas">{html_content}</div>' if two_columns else html_content
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body>{body}</body>
</html>"""


def generate_pdf_from_html(html_content: str, output_path: str = None, two_columns: bool = False) -> str:
    """Generates a PDF from HTML content.

    If two_columns is False (default), renders first without columns and
    checks the number of pages. If the result takes more than one page,
    automatically re-renders with two columns.

    Args:
        html_content: HTML fragment of the body to convert.
        output_path: Path of the output PDF file. If not provided,
                     a name is generated with the current date/time.
        two_columns: If True, uses the two-column layout directly.

    Returns:
        Path of the generated PDF file.
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"planning_{timestamp}.pdf"

    styles = [CSS(filename=str(_CSS_PATH))]

    if two_columns:
        HTML(string=_complete_html(html_content, two_columns=True)).write_pdf(
            output_path, stylesheets=styles
        )
        return output_path

    document = HTML(string=_complete_html(html_content, two_columns=False)).render(
        stylesheets=styles
    )
    if len(document.pages) > 1:
        print(f"PDF has {len(document.pages)} pages, regenerating with two columns...")
        HTML(string=_complete_html(html_content, two_columns=True)).write_pdf(
            output_path, stylesheets=styles
        )
    else:
        document.write_pdf(output_path)

    return output_path
