from __future__ import annotations
from urllib.parse import urlparse

ALLOWED_DOMAINS = {"altamino.top"}


def extract_url(text: str) -> str | None:
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None

    candidate = parts[1].strip()
    parsed = urlparse(candidate)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None

    return candidate


def is_altamino_link(url: str) -> bool:
    host = urlparse(url).hostname
    if not host:
        return False

    host = host.lower()
    return any(host == domain or host.endswith(f".{domain}") for domain in ALLOWED_DOMAINS)