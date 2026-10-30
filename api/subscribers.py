"""Weekly mail subscribers: email address + player tag, nothing else.

The list is one subscriber per line, `email,#TAG`. Blank lines and lines
starting with # are ignored; one address may appear with several tags. It
comes from the mail_subscribers env var (a GitHub secret in the workflow),
or locally from api/subscribers.csv (gitignored).
"""

import os

from config import SUBSCRIBERS_FILE

# Player tags only use these characters; people often type O for 0.
TAG_CHARS = set("0289PYLQGRJCUV")


def normalize_tag(tag: str) -> str:
    tag = tag.strip().upper().replace("O", "0").lstrip("#")
    if not tag or not set(tag) <= TAG_CHARS:
        raise ValueError(f"invalid player tag: {tag!r}")
    return f"#{tag}"


def parse_subscribers(text: str) -> list[dict]:
    """Parse the subscriber list; raises ValueError naming the bad line."""
    subscribers, seen = [], set()
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            email, tag = (part.strip() for part in line.split(","))
            if "@" not in email:
                raise ValueError(f"invalid email: {email!r}")
            entry = (email.lower(), normalize_tag(tag))
        except ValueError as e:
            raise ValueError(f"subscribers line {number}: {e}") from None
        if entry not in seen:
            seen.add(entry)
            subscribers.append({"email": entry[0], "tag": entry[1]})
    return subscribers


def load_subscribers() -> list[dict]:
    text = os.getenv("mail_subscribers")
    if text is None and os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            text = f.read()
    return parse_subscribers(text or "")
