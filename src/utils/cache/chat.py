from src import chat_cache
from src.utils.db import update_chat_settings


async def apply_chat_settings(event, **kwargs):
    s = await update_chat_settings(event.comId, event.message.chatId, **kwargs)
    entry = chat_cache.get((event.comId, event.message.chatId))
    if entry:
        entry["settings"] = s
    return s