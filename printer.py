import os
import socket

# Network printer configuration (read from the environment / .env)
PRINTER_HOST = os.getenv("PRINTER_HOST", "")
PRINTER_PORT = int(os.getenv("PRINTER_PORT", "9100"))


def print_pdf(pdf_path: str) -> None:
    """Sends a PDF to the network printer over a raw socket (port 9100).

    Uses the classic JetDirect/AppSocket method: the PDF bytes are sent
    as-is to the printer. The printer is defined by PRINTER_HOST (and
    optionally PRINTER_PORT) in the environment/.env.

    Raises:
        RuntimeError: If PRINTER_HOST is not configured.
    """
    if not PRINTER_HOST:
        raise RuntimeError(
            "PRINTER_HOST is not configured. Set it in the environment/.env"
        )

    with open(pdf_path, "rb") as f:
        data = f.read()

    with socket.create_connection((PRINTER_HOST, PRINTER_PORT), timeout=30) as sock:
        sock.sendall(data)

    print(f"Sent '{pdf_path}' to printer {PRINTER_HOST}:{PRINTER_PORT}")
