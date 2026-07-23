from __future__ import annotations

from functools import wraps

from src.utils.db import ChatSettings

from src import chat_cache

def _get_event(*args, **kwargs):
    return args[0] if args else kwargs.get("event") or kwargs.get("data")

def _get_uid(event) -> str | None:
    try:
        return event.message.author.uid
    except AttributeError:
        return None


async def _get_chat(event) -> dict | None:
    if not event.message.chatId:
        return None
    try:
        return chat_cache.get((event.comId, event.message.chatId))
    except Exception as e:
        return None




def ignore_yourself():
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            event = _get_event(*args, **kwargs)
            bot = event.client.userId

            if _get_uid(event) in (bot, None):
                return

            return await func(*args, **kwargs)
        return inner
    return decorator


def commands_enable_required():
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            event = _get_event(*args, **kwargs)
            chat = await _get_chat(event)
            if chat:
                settings: ChatSettings = chat.get("settings")
                if settings and not settings.commands_enabled:
                    return

            return await func(*args, **kwargs)
        return inner
    return decorator