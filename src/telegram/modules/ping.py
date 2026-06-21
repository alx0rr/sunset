from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message

from src.telegram import tgApp as app
from src.utils import ping_text


@app.on_message(filters.command("ping"))
async def ping_handler(_, message: Message):
    reply = await message.reply("🏓 Pinging...")
    latency_ms = (datetime.now() - message.date).total_seconds() * 1000
    await reply.edit_text("**🏓Pong!**\n\n" + ping_text(latency_ms))