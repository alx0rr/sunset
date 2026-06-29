from __future__ import annotations

from pyrogram import filters
from pyrogram.types import (
    Message
)
from src.telegram import tgApp as app
from src.telegram.helpers.wrappers import private_only
from src.utils.db import (
    get_language,
)
from src.utils.i18n import t



@app.on_message(filters.command("report") & filters.private)
@private_only
async def report_handler(_, message: Message):
    user_id = message.from_user.id
    lang = get_language(user_id)
    await message.reply(t("maintenance", lang))