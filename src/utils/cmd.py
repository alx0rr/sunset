from __future__ import annotations

def _parse_bool(value: str) -> bool | None:
    value = value.strip().lower()
    if value in ("on", "вкл", "1", "true", "да", "+"):
        return True
    if value in ("off", "выкл", "0", "false", "нет", "-"):
        return False
    return None


def _args(event) -> list[str]:
    """Everything after the command itself."""
    parts = event.message.content.split()
    return parts