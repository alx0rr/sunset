from __future__ import annotations

import asyncio
from functools import wraps

from altamino.objects.resp import Chat

from src.utils.roles import UserRole
from src.utils.i18n import t
from src import chat_cache


# ---------- helpers ----------

async def _send(event, text: str):
    if event.sub_client:
        await event.sub_client.send_message(
            event.message.chatId, text, event.message.messageId
        )
        return
    await event.client.send_message(
        event.message.chatId, text, event.message.messageId
    )


def _get_event(*args, **kwargs):
    return args[0] if args else kwargs.get("event") or kwargs.get("data")


def _get_role(event) -> int | None:
    try:
        return event.message.author.role
    except AttributeError:
        return None


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


async def check_chat_staff(event) -> bool:
    if _is_self(event):
        return True

    role = _get_role(event)
    if role is not None and UserRole.is_privileged_role(role):
        return True

    uid = _get_uid(event)
    chat = await _get_chat(event)
    return bool(uid and chat and is_chat_staff(chat.get("info"), uid))



# ---------- chat role checks ----------

def is_chat_host(chat: Chat, uid: str) -> bool:
    return chat is not None and chat.author.userId == uid


def is_chat_cohost(chat: Chat, uid: str) -> bool:
    return chat is not None and uid in (chat.coHosts or [])


def is_chat_staff(chat: Chat, uid: str) -> bool:
    return is_chat_host(chat, uid) or is_chat_cohost(chat, uid)


def _is_self(event) -> bool:
    return _get_uid(event) == event.client.userId

# ---------- wrapper factories ----------


def _make_wrapper(check, locale_key: str = "errors.no_permission"):
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            event = _get_event(*args, **kwargs)

            if _is_self(event):
                return await func(*args, **kwargs)

            role = _get_role(event)
            if role is None or not check(role):
                await _send(event, t(locale_key, comId=event.comId))
                return

            return await func(*args, **kwargs)
        return inner
    return decorator


def _make_chat_wrapper(chat_check, locale_key: str = "errors.no_permission"):
    def decorator(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            event = _get_event(*args, **kwargs)

            if _is_self(event):
                return await func(*args, **kwargs)

            role = _get_role(event)
            if role is not None and UserRole.is_privileged_role(role):
                return await func(*args, **kwargs)

            uid = _get_uid(event)
            chat = await _get_chat(event)
            if uid and chat and chat_check(chat.get("info"), uid):
                return await func(*args, **kwargs)

            await _send(event, t(locale_key, comId=event.comId))
        return inner
    return decorator

require_privileged = _make_wrapper(UserRole.is_privileged_role)
require_local_staff = _make_wrapper(UserRole.is_local_staff)
require_local_admin = _make_wrapper(
    UserRole.is_local_admin, "errors.no_permission_admin"
)
require_global_staff = _make_wrapper(
    UserRole.is_global_staff, "errors.no_permission_global"
)


def require_min_role(min_role: int, locale_key: str = "errors.no_permission"):
    return _make_wrapper(lambda r: r >= min_role, locale_key)


def require_role(*roles: int, locale_key: str = "errors.no_permission"):
    allowed = set(roles)
    return _make_wrapper(lambda r: r in allowed, locale_key)


# ---------- chat-level decorators ----------

require_chat_host = _make_chat_wrapper(is_chat_host, "errors.no_permission_host")
require_chat_staff = _make_chat_wrapper(is_chat_staff, "errors.no_permission_chat")