from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from src.telegram import tgApp as app
from src.utils import ping_text
from src.telegram.modules.adm import on_set_altaminoid
from src.utils.db import get_language
from src.utils.i18n import t


@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    reply = await message.reply("🏓 Pinging...")
    latency_ms = (datetime.now() - message.date).total_seconds() * 1000
    await reply.edit_text("**🏓Pong!**\n\n" + ping_text(latency_ms))


@app.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    if len(message.command) > 1 and message.command[1] == "setAltAmino":
        await on_set_altaminoid(message)
        return
    
    lang = get_language(message.from_user.id)
    await message.reply(t('telegram.welcome', lang))