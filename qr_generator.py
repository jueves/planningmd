from datetime import datetime
from urllib.parse import quote

import qrcode
import qrcode.image.svg


def build_created_after_url(moment: datetime) -> str:
    """Builds a Todoist search URL for tasks created after the given moment.

    Opening the URL in a browser runs the search in the Todoist web app.
    """
    query = f"created after: {moment.strftime('%m/%d/%Y %H:%M')}"
    return f"https://app.todoist.com/app/search/{quote(query, safe='')}"


def generate_qr_svg(data: str) -> str:
    """Returns an SVG string with a QR code encoding the given data."""
    image = qrcode.make(
        data,
        image_factory=qrcode.image.svg.SvgPathImage,
        border=0,
    )
    return image.to_string(encoding="unicode")
