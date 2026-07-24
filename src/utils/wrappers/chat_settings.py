from __future__ import annotations

from functools import wraps

from src.utils.db import ChatSettings
from altamino import respObject, args
from src.utils.i18n import t

from src import chat_cache

def _get_event(*args, **kwargs):
    return args[0] if args else kwargs.get("event") or kwargs.get("data")

def _get_uid(event) -> str | None:
    try:
        return event.message.author.userId
    except AttributeError:
        return None


async def _get_chat(event) -> dict | None:
    if not event.message.chatId:
        return None
    try:
        return chat_cache.get((event.comId, event.message.chatId))
    except Exception as e:
        return None


async def _send(event, text: str):
    if event.sub_client:
        await event.sub_client.send_message(
            event.message.chatId, text, event.message.messageId
        )
        return
    await event.client.send_message(
        event.message.chatId, text, event.message.messageId
    )

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


def chat_type_required(chatTypes: list[int] = [], locale_key: str | None = None):
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            event = _get_event(*args, **kwargs)
            chat = await _get_chat(event)
            if chat:
                info: respObject.Chat = chat.get("info")
                if info and chatTypes and info.type not in chatTypes:
                    if locale_key:
                        await _send(event, t(locale_key, comId=event.comId))
                    return

            return await func(*args, **kwargs)
        return inner
    return decorator


require_group_chat = chat_type_required([args.ChatTypes.Group])
require_private_chat = chat_type_required([args.ChatTypes.Private])
require_public_chat = chat_type_required([args.ChatTypes.Public])