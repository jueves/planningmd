import random
from pathlib import Path

_QUOTES_PATH = Path(__file__).parent / "quotes.md"


def get_random_quote() -> str | None:
    """Parses quotes.md and returns a random quote as a string.

    Quotes are standard markdown blockquotes (lines starting with '>').
    Returns None if no quotes are found.
    """
    text = _QUOTES_PATH.read_text(encoding="utf-8")

    quotes = []
    current: list[str] = []

    for line in text.splitlines():
        if line.startswith('>'):
            current.append(line[1:].lstrip())
        elif current:
            quotes.append('\n'.join(current).strip())
            current = []

    if current:
        quotes.append('\n'.join(current).strip())

    quotes = [q for q in quotes if q]

    if not quotes:
        return None

    return random.choice(quotes)
