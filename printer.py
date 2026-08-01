import os
import struct
from urllib.parse import urlparse

import requests

# Network printer configuration (read from the environment / .env)
#   PRINTER_URI       IPP URI of the network printer, e.g.
#                     ipp://192.168.1.50:631/ipp/print
#   PRINTER_JOB_USER  Name attached to the print job (optional)
PRINTER_URI = os.getenv("PRINTER_URI", "")
PRINTER_JOB_USER = os.getenv("PRINTER_JOB_USER", "planningmd")

# IPP protocol constants
_IPP_VERSION = (2, 0)
_OP_PRINT_JOB = 0x0002
_TAG_OPERATION_ATTRS = 0x01
_TAG_END_ATTRS = 0x03
_TAG_CHARSET = 0x47
_TAG_NATURAL_LANG = 0x48
_TAG_URI = 0x45
_TAG_NAME = 0x42          # nameWithoutLanguage
_TAG_MIME = 0x49          # mimeMediaType
_IPP_STATUS_ERROR_FLOOR = 0x0100  # status codes >= this are errors


def _attribute(tag: int, name: bytes, value: bytes) -> bytes:
    """Encodes a single IPP attribute (tag + name + value)."""
    return (
        struct.pack(">B", tag)
        + struct.pack(">H", len(name)) + name
        + struct.pack(">H", len(value)) + value
    )


def _build_print_job_request(printer_uri: str, job_name: str) -> bytes:
    """Builds the binary IPP Print-Job request (without the document data)."""
    header = struct.pack(
        ">BBHI", _IPP_VERSION[0], _IPP_VERSION[1], _OP_PRINT_JOB, 1
    )

    attrs = struct.pack(">B", _TAG_OPERATION_ATTRS)
    attrs += _attribute(_TAG_CHARSET, b"attributes-charset", b"utf-8")
    attrs += _attribute(_TAG_NATURAL_LANG, b"attributes-natural-language", b"en")
    attrs += _attribute(_TAG_URI, b"printer-uri", printer_uri.encode())
    attrs += _attribute(_TAG_NAME, b"requesting-user-name", PRINTER_JOB_USER.encode())
    attrs += _attribute(_TAG_NAME, b"job-name", job_name.encode())
    attrs += _attribute(_TAG_MIME, b"document-format", b"application/pdf")
    attrs += struct.pack(">B", _TAG_END_ATTRS)

    return header + attrs


def _http_url(printer_uri: str) -> str:
    """Maps an ipp(s):// printer URI to the http(s):// URL used to POST to it."""
    parsed = urlparse(printer_uri)
    scheme = "https" if parsed.scheme == "ipps" else "http"
    port = parsed.port or 631
    path = parsed.path or "/"
    return f"{scheme}://{parsed.hostname}:{port}{path}"


def print_pdf(pdf_path: str, job_name: str = "planning") -> None:
    """Sends a PDF file to the configured network printer via IPP.

    The printer is defined by the PRINTER_URI environment variable. Any
    modern network printer that supports IPP Everywhere accepts PDF
    documents directly, so no driver or CUPS server is required.

    Args:
        pdf_path: Path of the PDF file to print.
        job_name: Name shown for the print job on the printer.

    Raises:
        RuntimeError: If PRINTER_URI is not configured or the printer
                      rejects the job.
    """
    if not PRINTER_URI:
        raise RuntimeError(
            "PRINTER_URI is not configured. Set it in the environment/.env, "
            "e.g. PRINTER_URI=ipp://192.168.1.50:631/ipp/print"
        )

    with open(pdf_path, "rb") as f:
        document = f.read()

    body = _build_print_job_request(PRINTER_URI, job_name) + document
    url = _http_url(PRINTER_URI)

    response = requests.post(
        url,
        data=body,
        headers={"Content-Type": "application/ipp"},
        timeout=30,
    )
    response.raise_for_status()

    # The IPP status-code is a 2-byte field at offset 2 of the response.
    if len(response.content) < 4:
        raise RuntimeError("Printer returned an invalid IPP response")
    status_code = struct.unpack(">H", response.content[2:4])[0]
    if status_code >= _IPP_STATUS_ERROR_FLOOR:
        raise RuntimeError(
            f"Printer rejected the job (IPP status 0x{status_code:04x})"
        )

    print(f"Sent '{pdf_path}' to printer at {PRINTER_URI}")
