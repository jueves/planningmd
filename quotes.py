import random
import re
from pathlib import Path

_QUOTES_PATH = Path(__file__).parent / "quotes.md"


def get_random_quote() -> str | None:
    """Parses quotes.md and returns a random quote as a string.

    Quotes are blocks of text between two lines of 3+ hyphens.
    Returns None if no quotes are found.
    """
    text = _QUOTES_PATH.read_text(encoding="utf-8")

    blocks = re.split(r'(?m)^-{3,}\s*$', text)

    # The first block is introductory text before any separator; skip it
    quotes = [b.strip() for b in blocks[1:] if b.strip()]

    if not quotes:
        return None

    return random.choice(quotes)
