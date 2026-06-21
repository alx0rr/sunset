import time
from datetime import timedelta

from src.config import STARTUP


def ping_text(latency_ms: float) -> str:
    uptime = timedelta(seconds=int(time.time() - STARTUP))

    return (
        f"⏱ Latency: `{latency_ms:.0f} ms`\n"
        f"🕒 Uptime: `{uptime}`"
    )