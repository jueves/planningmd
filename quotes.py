import random
import re
from pathlib import Path

_QUOTES_PATH = Path(__file__).parent / "quotes.md"


def get_random_quote() -> dict | None:
    """Parses quotes.md and returns a random quote as a dict with 'text' and 'author' keys.

    Quotes are blocks of text between two lines of 3+ hyphens.
    The author is the text after an em dash (—), if present.
    Returns None if no quotes are found.
    """
    text = _QUOTES_PATH.read_text(encoding="utf-8")

    # Split on lines containing only 3+ hyphens
    blocks = re.split(r'(?m)^-{3,}\s*$', text)

    # The first block is introductory text before any separator; skip it
    quotes = []
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue

        author_match = re.search(r'—\s*(.+)', block)
        author = author_match.group(1).strip() if author_match else None

        # Remove the author line to get the quote text, stripping surrounding quotes
        quote_text = re.sub(r'—\s*.+', '', block).strip()
        quote_text = re.sub(r'^["\u201c]+|["\u201d]+$', '', quote_text).strip()

        if quote_text:
            quotes.append({"text": quote_text, "author": author})

    if not quotes:
        return None

    return random.choice(quotes)
