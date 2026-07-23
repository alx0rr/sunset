import time
from datetime import timedelta

from src.config import STARTUP
from altamino import respObject
import string

def ping_text(latency_ms: float) -> str:
    uptime = timedelta(seconds=int(time.time() - STARTUP))

    return (
        f"⏱ Latency: `{latency_ms:.0f} ms`\n"
        f"🕒 Uptime: `{uptime}`"
    )


async def reply(event: respObject.Event, text: str, mentionUserIds: list[str] = [], reply: bool = True):
    target = event.sub_client or event.client
    await target.send_message(event.message.chatId, text, event.message.messageId if reply else None, mentionUserIds=mentionUserIds)


def safe_format(tpl: str, **kwargs) -> str:
    return string.Formatter().vformat(tpl, (), _SafeDict(kwargs))


class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"