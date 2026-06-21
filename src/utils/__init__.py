import time
from datetime import timedelta
from src.config import STARTUP

def ping_text():
    start = time.monotonic()
    latency = (time.monotonic() - start) * 1000

    uptime = timedelta(seconds=int(time.time() - STARTUP))

    return (
        f"⏱ Latency: `{latency:.0f} ms`\n"
        f"🕒 Uptime: `{uptime}`"
    )