from __future__ import annotations
from functools import wraps
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatType
from src.utils.db import get_language
from src.utils.i18n import t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def private_only(func):
    @wraps(func)
    async def wrapper(client, update: Message | CallbackQuery, *args, **kwargs):
        message = update if isinstance(update, Message) else update.message
        if message.chat.type != ChatType.PRIVATE:
            lang = get_language(update.from_user.id)
            text = t("telegram.private_only", lang)
            if isinstance(update, CallbackQuery):
                await update.answer(text, show_alert=True)
            else:
                me = await client.get_me()
                await update.reply(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(t("telegram.open_direct", lang), url=f"https://t.me/{me.username}")],
                ]))
            return
        await func(client, update)
    return wrapper