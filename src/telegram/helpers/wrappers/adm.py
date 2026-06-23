from __future__ import annotations

from src.config import  OWNER_IDS
from src.utils.db import admin_exists
from functools import wraps
from pyrogram.types import Message, CallbackQuery

from src.utils.db import get_language
from src.utils.i18n import t


def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


def is_admin(user_id: int) -> bool:
    return is_owner(user_id) or admin_exists(user_id)


def admin_only(func):
    @wraps(func)
    async def wrapper(client, update: Message | CallbackQuery):
        user_id = update.from_user.id
        if not is_admin(user_id):
            lang = get_language(user_id)
            text = t("telegram.admin_only", lang)
            if isinstance(update, CallbackQuery):
                await update.answer(text, show_alert=True)
            else:
                await update.reply(text)
            return
        await func(client, update)
    return wrapper


def owner_only(func):
    @wraps(func)
    async def wrapper(client, update: Message | CallbackQuery):
        user_id = update.from_user.id
        if not is_owner(user_id):
            lang = get_language(user_id)
            text = t("telegram.owner_only", lang)
            if isinstance(update, CallbackQuery):
                await update.answer(text, show_alert=True)
            else:
                await update.reply(text)
            return
        await func(client, update)
    return wrapper


