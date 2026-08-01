import os
import subprocess

# CUPS printer configuration (read from the environment / .env)
#   CUPS_SERVER   Host (or host:port) of the CUPS server. Port defaults to
#                 631 (IPP). Leave empty to use the local CUPS instance.
#   PRINTER_NAME  Name of the print queue on that CUPS server.
CUPS_SERVER = os.getenv("CUPS_SERVER", "")
PRINTER_NAME = os.getenv("PRINTER_NAME", "")


def print_pdf(pdf_path: str) -> None:
    """Sends a PDF to a print queue on a CUPS server via `lp` (IPP, port 631).

    CUPS handles the queue, drivers and format conversion; this just hands
    it the PDF and the target queue name. The queue is defined by
    PRINTER_NAME, and the server (if remote) by CUPS_SERVER, in the .env.

    Raises:
        RuntimeError: If PRINTER_NAME is not configured or `lp` fails.
    """
    if not PRINTER_NAME:
        raise RuntimeError(
            "PRINTER_NAME is not configured. Set it in the environment/.env"
        )

    env = dict(os.environ)
    if CUPS_SERVER:
        env["CUPS_SERVER"] = CUPS_SERVER

    result = subprocess.run(
        ["lp", "-d", PRINTER_NAME, pdf_path],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"lp failed: {result.stderr.strip() or result.stdout.strip()}"
        )

    where = CUPS_SERVER or "local CUPS"
    print(f"Sent '{pdf_path}' to '{PRINTER_NAME}' on {where}: {result.stdout.strip()}")
