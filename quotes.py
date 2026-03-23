import random
import re
from pathlib import Path

_QUOTES_PATH = Path(__file__).parent / "quotes.md"


def get_random_quote() -> dict | None:
    """Parses quotes.md and returns a random quote as a dict with 'text' and 'author' keys.

    Returns None if no valid quotes are found.
    """
    text = _QUOTES_PATH.read_text(encoding="utf-8")

    # Split on blocks of 3 or more hyphens
    blocks = re.split(r'-{3,}', text)

    quotes = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Look for text in double quotes (may span multiple lines)
        quote_match = re.search(r'"([^"]+)"', block, re.DOTALL)
        if not quote_match:
            continue

        quote_text = quote_match.group(1).strip()

        # Look for an author preceded by an em dash (—)
        author_match = re.search(r'—\s*(.+)', block)
        author = author_match.group(1).strip() if author_match else None

        quotes.append({"text": quote_text, "author": author})

    if not quotes:
        return None

    return random.choice(quotes)
