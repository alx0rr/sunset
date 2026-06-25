from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.types import Message

from src.telegram import tgApp as app
from src.telegram.modules.adm import on_set_altaminoid
from src.utils import ping_text
from src.utils.db import get_language
from src.utils.i18n import t
from src.telegram.helpers.wrappers.adm import is_admin

@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    start = datetime.now(timezone.utc)
    reply = await message.reply("🏓 Pinging...")
    latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    await reply.edit_text("**🏓Pong!**\n\n" + ping_text(latency_ms))

@app.on_message(filters.command("help"))
async def help_handler(_, message: Message):
    lang = get_language(message.from_user.id)
    await message.reply(t("telegram.help", lang))

@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    if len(message.command) > 1 and message.command[1] == "setAltAmino":
        if not is_admin(message.from_user.id):
            lang = get_language(message.from_user.id)
            await message.reply(t("telegram.admin_only", lang))
            return
        await on_set_altaminoid(message)
        return

    lang = get_language(message.from_user.id)
    await message.reply(t("telegram.welcome", lang))
