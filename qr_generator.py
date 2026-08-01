from datetime import datetime
from urllib.parse import quote

import qrcode
import qrcode.image.svg


def build_created_after_url(moment: datetime, target: str = "app") -> str:
    """Builds a Todoist search URL for tasks created after the given moment.

    Args:
        moment: Search for tasks created after this datetime.
        target: "app" builds a todoist:// deep link that opens the search in
                the mobile app; "web" builds an https URL for the web app.
    """
    if target not in ("app", "web"):
        raise ValueError(f"Invalid QR target: {target!r} (expected 'app' or 'web')")
    query = quote(f"created after: {moment.strftime('%d/%m/%Y %H:%M')}", safe="")
    if target == "app":
        return f"todoist://search?query={query}"
    return f"https://app.todoist.com/app/search/{query}"


def generate_qr_svg(data: str) -> str:
    """Returns an SVG string with a QR code encoding the given data."""
    image = qrcode.make(
        data,
        image_factory=qrcode.image.svg.SvgPathImage,
        border=0,
    )
    return image.to_string(encoding="unicode")
